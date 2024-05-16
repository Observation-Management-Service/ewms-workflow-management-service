"""Test the MQS scheduling logic with the workflow_mq_activator module/daemon.

Runs everything in main process and thread. Uses a real mongo database
and mock/patched MQS REST calls."""

import asyncio
import logging
import time
from typing import Any, Iterator
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from wms import database, config, schema, workflow_mq_activator

logging.getLogger("pymongo").setLevel(logging.INFO)

TEST_WORKFLOWS = [
    dict(
        workflow_id=workflow_id,
        timestamp=1 + i,
        priority=10,
        mq_activated_ts=None,
        _mqs_retry_at_ts=config.MQS_RETRY_AT_TS_DEFAULT_VALUE,
        aborted=False,
    )
    for i, workflow_id in enumerate(["A1", "B2", "C3", "D4", "E5"])
]


def _make_test_task_directives(workflow: dict, n_tds: int) -> Iterator[dict]:
    for n in range(n_tds + 1):
        yield dict(
            task_id=f"td-{n}",
            workflow_id=workflow["workflow_id"],
            #
            cluster_locations=["foo", "bar"],
            task_image="bap",
            task_args="--baz bat",
            timestamp=1 + n,
            #
            input_queues=[f"q-td-{n}-in"],
            output_queues=[f"q-td-{n}-out"],
        )


def _make_test_taskforce(task_directive: dict, location: str, i: int) -> dict:
    return dict(
        taskforce_uuid=f"{task_directive['task_id']}-{i}",
        task_id=task_directive["task_id"],
        workflow_id=task_directive["workflow_id"],
        #
        timestamp=task_directive["timestamp"],
        collector=f"collector-{location}",
        schedd=f"schedd-{location}",
        n_workers=100,
        container_config=dict(
            image=task_directive["task_image"],
            arguments=task_directive["task_args"],
            environment={},
            input_files=[],
        ),
        worker_config=dict(
            do_transfer_worker_stdouterr=True,
            max_worker_runtime=60 * 10,
            n_cores=1,
            priority=99,
            worker_disk="512M",
            worker_memory="512M",
        ),
        cluster_id=None,
        submit_dict={},
        job_event_log_fpath="",
        condor_complete_ts=None,
        phase=schema.enums.TaskforcePhase.PRE_MQ_ASSEMBLY,
        compound_statuses={},
        top_task_errors={},
    )


class MQSRESTCalls:
    call_ct = -1  # class var
    last_ts = 0.0
    retry_dues: dict[str, float] = {}

    @staticmethod
    def request_activation_to_mqs(_: Any, workflow: dict) -> dict:
        assert workflow

        diff = time.time() - MQSRESTCalls.last_ts
        MQSRESTCalls.last_ts = time.time()
        MQSRESTCalls.call_ct += 1

        match MQSRESTCalls.call_ct:
            # accept A
            case 0:
                assert workflow["workflow_id"] == "A1"
                # assert config.ENV.TASK_MQ_ASSEMBLY_DELAY <= diff <= config.ENV.TASK_MQ_ASSEMBLY_DELAY+1  # check won't work for first call
                return dict(
                    mqprofiles=[
                        dict(mqid=f"100-{workflow['task_id']}"),
                        dict(mqid=f"200-{workflow['task_id']}"),
                    ]
                )
            # deny B
            case 1:
                assert workflow["workflow_id"] == "B2"
                assert (
                    config.ENV.TASK_MQ_ASSEMBLY_DELAY
                    <= diff
                    <= config.ENV.TASK_MQ_ASSEMBLY_DELAY + 1
                )
                MQSRESTCalls.retry_dues[workflow["workflow_id"]] = (
                    time.time() + config.ENV.TASK_MQ_ASSEMBLY_MQS_RETRY_WAIT
                )
                return dict(try_again_later=True)
            # accept C
            case 2:
                assert workflow["workflow_id"] == "C3"
                assert (  # prev was denied AND this one was accepted, so this was a short sleep
                    config.TASK_MQ_ASSEMBLY_SHORTEST_SLEEP
                    <= diff
                    <= config.TASK_MQ_ASSEMBLY_SHORTEST_SLEEP + 1
                )
                return dict(
                    mqprofiles=[
                        dict(mqid=f"100-{workflow['task_id']}"),
                        dict(mqid=f"200-{workflow['task_id']}"),
                    ]
                )
            # accept D
            case 3:
                assert workflow["workflow_id"] == "D4"
                assert (
                    config.ENV.TASK_MQ_ASSEMBLY_DELAY
                    <= diff
                    <= config.ENV.TASK_MQ_ASSEMBLY_DELAY + 1
                )
                return dict(
                    mqprofiles=[
                        dict(mqid=f"100-{workflow['task_id']}"),
                        dict(mqid=f"200-{workflow['task_id']}"),
                    ]
                )
            # deny E
            case 4:
                assert workflow["workflow_id"] == "E5"
                assert (
                    config.ENV.TASK_MQ_ASSEMBLY_DELAY
                    <= diff
                    <= config.ENV.TASK_MQ_ASSEMBLY_DELAY + 1
                )
                MQSRESTCalls.retry_dues[workflow["workflow_id"]] = (
                    time.time() + config.ENV.TASK_MQ_ASSEMBLY_MQS_RETRY_WAIT
                )
                return dict(try_again_later=True)
            # retry: re-deny B
            case 5:
                assert workflow["workflow_id"] == "B2"
                assert (
                    MQSRESTCalls.retry_dues[workflow["workflow_id"]]
                    <= time.time()
                    <= MQSRESTCalls.retry_dues[workflow["workflow_id"]] + 2
                )
                MQSRESTCalls.retry_dues[workflow["workflow_id"]] = (
                    time.time() + config.ENV.TASK_MQ_ASSEMBLY_MQS_RETRY_WAIT
                )
                return dict(try_again_later=True)
            # retry: re-deny E
            case 6:
                assert workflow["workflow_id"] == "E5"
                assert (
                    MQSRESTCalls.retry_dues[workflow["workflow_id"]]
                    <= time.time()
                    <= MQSRESTCalls.retry_dues[workflow["workflow_id"]] + 2
                )
                MQSRESTCalls.retry_dues[workflow["workflow_id"]] = (
                    time.time() + config.ENV.TASK_MQ_ASSEMBLY_MQS_RETRY_WAIT
                )
                return dict(try_again_later=True)
            # retry: re-deny B
            case 7:
                assert workflow["workflow_id"] == "B2"
                assert (
                    MQSRESTCalls.retry_dues[workflow["workflow_id"]]
                    <= time.time()
                    <= MQSRESTCalls.retry_dues[workflow["workflow_id"]] + 2
                )
                MQSRESTCalls.retry_dues[workflow["workflow_id"]] = (
                    time.time() + config.ENV.TASK_MQ_ASSEMBLY_MQS_RETRY_WAIT
                )
                return dict(try_again_later=True)
            # retry: accept E
            case 8:
                assert workflow["workflow_id"] == "E5"
                assert (
                    MQSRESTCalls.retry_dues[workflow["workflow_id"]]
                    <= time.time()
                    <= MQSRESTCalls.retry_dues[workflow["workflow_id"]] + 2
                )
                return dict(
                    mqprofiles=[
                        dict(mqid=f"100-{workflow['task_id']}"),
                        dict(mqid=f"200-{workflow['task_id']}"),
                    ]
                )
            # retry: re-deny B
            case 9:
                assert workflow["workflow_id"] == "B2"
                assert (
                    MQSRESTCalls.retry_dues[workflow["workflow_id"]]
                    <= time.time()
                    <= MQSRESTCalls.retry_dues[workflow["workflow_id"]] + 2
                )
                MQSRESTCalls.retry_dues[workflow["workflow_id"]] = (
                    time.time() + config.ENV.TASK_MQ_ASSEMBLY_MQS_RETRY_WAIT
                )
                return dict(try_again_later=True)
            # retry: accept B
            case 10:
                assert workflow["workflow_id"] == "B2"
                assert (
                    MQSRESTCalls.retry_dues[workflow["workflow_id"]]
                    <= time.time()
                    <= MQSRESTCalls.retry_dues[workflow["workflow_id"]] + 2
                )
                return dict(
                    mqprofiles=[
                        dict(mqid=f"100-{workflow['task_id']}"),
                        dict(mqid=f"200-{workflow['task_id']}"),
                    ]
                )
            # ???
            case other:
                print(other)
                assert 0


def _make_post_mqs_loop_taskforce(task_directive: dict, location: str, i: int) -> dict:
    taskforce = _make_test_taskforce(task_directive, location, i)
    taskforce["container_config"].update(
        {
            "environment": {
                "EWMS_PILOT_QUEUE_INCOMING": f"100-{task_directive['task_id']}",
                "EWMS_PILOT_QUEUE_OUTGOING": f"200-{task_directive['task_id']}",
            }
        }
    )
    taskforce["phase"] = str(schema.enums.TaskforcePhase.PRE_LAUNCH)
    return taskforce


@patch("wms.workflow_mq_activator.request_activation_to_mqs", new_callable=AsyncMock)
@patch("wms.workflow_mq_activator.RestClient", new=MagicMock)  # it's a from-import
async def test_000(mock_req_act_to_mqs: AsyncMock) -> None:
    """Test the MQS scheduling with several tasks and requests."""
    mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")
    workflows_client = database.client.WMSMongoClient(
        mongo_client,
        database.utils.WORKFLOWS_COLL_NAME,
    )
    task_directives_client = database.client.WMSMongoClient(
        mongo_client,
        database.utils.TASK_DIRECTIVES_COLL_NAME,
    )
    taskforces_client = database.client.WMSMongoClient(
        mongo_client,
        database.utils.TASKFORCES_COLL_NAME,
    )

    # ingest data into mongo as if REST user did so
    for i, wf in enumerate(TEST_WORKFLOWS):
        await workflows_client.insert_one(wf)
        for td in _make_test_task_directives(wf, i):
            await task_directives_client.insert_one(td)
            for j, location in enumerate(td["cluster_locations"]):  # type: ignore
                await taskforces_client.insert_one(
                    _make_test_taskforce(td, location, j)
                )

    # pre-patch all the REST calls to MQS
    mock_req_act_to_mqs.side_effect = MQSRESTCalls.request_activation_to_mqs

    # go!
    with pytest.raises(asyncio.TimeoutError):
        # use asyncio's timeout to artificially stop loop, otherwise it'd go forever
        await asyncio.wait_for(workflow_mq_activator.startup(mongo_client), timeout=60)

    # check mongo db state
    wfs_in_db = [t async for t in workflows_client.find_all({}, [])]
    # look at workflows
    assert len(wfs_in_db) == len(TEST_WORKFLOWS)
    # now, individually
    for wf in wfs_in_db:
        src = next(  # using 'next' gives shorter debug than w/ 'in'
            wf for wf in TEST_WORKFLOWS if wf["workflow_id"] == wf["workflow_id"]
        )
        # ignore the '_mqs_retry_at_ts' key, it's functionality is tested by MQSRESTCalls.request_activation_to_mqs
        assert {k: v for k, v in wf.items() if k != "_mqs_retry_at_ts"} == {
            **{k: v for k, v in src.items() if k != "_mqs_retry_at_ts"},
            "queues": [f"100-{wf['workflow_id']}", f"200-{wf['workflow_id']}"],
        }
        # look at taskforces
        tfs_in_db = [
            t async for t in taskforces_client.find_all(dict(task_id=wf["task_id"]), [])
        ]
        assert tfs_in_db == [  # type: ignore
            _make_post_mqs_loop_taskforce(wf, location, i)
            for i, location in enumerate(wf["cluster_locations"])  # type: ignore
        ]
