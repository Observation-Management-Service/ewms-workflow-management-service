"""Test the MQS scheduling logic with the workflow_mq_activator module/daemon.

Runs everything in main process and thread. Uses a real mongo database
and mock/patched MQS REST calls."""

import asyncio
import logging
import time
from typing import Any
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from wms import database, config, schema, workflow_mq_activator

logging.getLogger("pymongo").setLevel(logging.INFO)


TEST_TASK_DIRECTIVES = [
    dict(
        task_id=task_id,
        cluster_locations=["foo", "bar"],
        task_image="bap",
        task_args="--baz bat",
        timestamp=1 + i,
        priority=10,
        #
        n_queues=2,
        queues=[],
        _mqs_retry_at_ts=config.MQS_RETRY_AT_TS_DEFAULT_VALUE,
        #
        aborted=False,
    )
    for i, task_id in enumerate(["A1", "B2", "C3", "D4", "E5"])
]


def _make_test_taskforce(task_directive: dict, location: str, i: int) -> dict:
    return dict(
        taskforce_uuid=f"{task_directive['task_id']}-{i}",
        task_id=task_directive["task_id"],
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
    def request_to_mqs(_: Any, task_directive: dict) -> dict:
        assert task_directive

        diff = time.time() - MQSRESTCalls.last_ts
        MQSRESTCalls.last_ts = time.time()
        MQSRESTCalls.call_ct += 1

        match MQSRESTCalls.call_ct:
            # accept A
            case 0:
                assert task_directive["task_id"] == "A1"
                # assert config.ENV.TASK_MQ_ASSEMBLY_DELAY <= diff <= config.ENV.TASK_MQ_ASSEMBLY_DELAY+1  # check won't work for first call
                return dict(
                    mqprofiles=[
                        dict(mqid=f"100-{task_directive['task_id']}"),
                        dict(mqid=f"200-{task_directive['task_id']}"),
                    ]
                )
            # deny B
            case 1:
                assert task_directive["task_id"] == "B2"
                assert (
                    config.ENV.TASK_MQ_ASSEMBLY_DELAY
                    <= diff
                    <= config.ENV.TASK_MQ_ASSEMBLY_DELAY + 1
                )
                MQSRESTCalls.retry_dues[task_directive["task_id"]] = (
                    time.time() + config.ENV.TASK_MQ_ASSEMBLY_MQS_RETRY_WAIT
                )
                return dict(try_again_later=True)
            # accept C
            case 2:
                assert task_directive["task_id"] == "C3"
                assert (  # prev was denied AND this one was accepted, so this was a short sleep
                    config.TASK_MQ_ASSEMBLY_SHORTEST_SLEEP
                    <= diff
                    <= config.TASK_MQ_ASSEMBLY_SHORTEST_SLEEP + 1
                )
                return dict(
                    mqprofiles=[
                        dict(mqid=f"100-{task_directive['task_id']}"),
                        dict(mqid=f"200-{task_directive['task_id']}"),
                    ]
                )
            # accept D
            case 3:
                assert task_directive["task_id"] == "D4"
                assert (
                    config.ENV.TASK_MQ_ASSEMBLY_DELAY
                    <= diff
                    <= config.ENV.TASK_MQ_ASSEMBLY_DELAY + 1
                )
                return dict(
                    mqprofiles=[
                        dict(mqid=f"100-{task_directive['task_id']}"),
                        dict(mqid=f"200-{task_directive['task_id']}"),
                    ]
                )
            # deny E
            case 4:
                assert task_directive["task_id"] == "E5"
                assert (
                    config.ENV.TASK_MQ_ASSEMBLY_DELAY
                    <= diff
                    <= config.ENV.TASK_MQ_ASSEMBLY_DELAY + 1
                )
                MQSRESTCalls.retry_dues[task_directive["task_id"]] = (
                    time.time() + config.ENV.TASK_MQ_ASSEMBLY_MQS_RETRY_WAIT
                )
                return dict(try_again_later=True)
            # retry: re-deny B
            case 5:
                assert task_directive["task_id"] == "B2"
                assert (
                    MQSRESTCalls.retry_dues[task_directive["task_id"]]
                    <= time.time()
                    <= MQSRESTCalls.retry_dues[task_directive["task_id"]] + 2
                )
                MQSRESTCalls.retry_dues[task_directive["task_id"]] = (
                    time.time() + config.ENV.TASK_MQ_ASSEMBLY_MQS_RETRY_WAIT
                )
                return dict(try_again_later=True)
            # retry: re-deny E
            case 6:
                assert task_directive["task_id"] == "E5"
                assert (
                    MQSRESTCalls.retry_dues[task_directive["task_id"]]
                    <= time.time()
                    <= MQSRESTCalls.retry_dues[task_directive["task_id"]] + 2
                )
                MQSRESTCalls.retry_dues[task_directive["task_id"]] = (
                    time.time() + config.ENV.TASK_MQ_ASSEMBLY_MQS_RETRY_WAIT
                )
                return dict(try_again_later=True)
            # retry: re-deny B
            case 7:
                assert task_directive["task_id"] == "B2"
                assert (
                    MQSRESTCalls.retry_dues[task_directive["task_id"]]
                    <= time.time()
                    <= MQSRESTCalls.retry_dues[task_directive["task_id"]] + 2
                )
                MQSRESTCalls.retry_dues[task_directive["task_id"]] = (
                    time.time() + config.ENV.TASK_MQ_ASSEMBLY_MQS_RETRY_WAIT
                )
                return dict(try_again_later=True)
            # retry: accept E
            case 8:
                assert task_directive["task_id"] == "E5"
                assert (
                    MQSRESTCalls.retry_dues[task_directive["task_id"]]
                    <= time.time()
                    <= MQSRESTCalls.retry_dues[task_directive["task_id"]] + 2
                )
                return dict(
                    mqprofiles=[
                        dict(mqid=f"100-{task_directive['task_id']}"),
                        dict(mqid=f"200-{task_directive['task_id']}"),
                    ]
                )
            # retry: re-deny B
            case 9:
                assert task_directive["task_id"] == "B2"
                assert (
                    MQSRESTCalls.retry_dues[task_directive["task_id"]]
                    <= time.time()
                    <= MQSRESTCalls.retry_dues[task_directive["task_id"]] + 2
                )
                MQSRESTCalls.retry_dues[task_directive["task_id"]] = (
                    time.time() + config.ENV.TASK_MQ_ASSEMBLY_MQS_RETRY_WAIT
                )
                return dict(try_again_later=True)
            # retry: accept B
            case 10:
                assert task_directive["task_id"] == "B2"
                assert (
                    MQSRESTCalls.retry_dues[task_directive["task_id"]]
                    <= time.time()
                    <= MQSRESTCalls.retry_dues[task_directive["task_id"]] + 2
                )
                return dict(
                    mqprofiles=[
                        dict(mqid=f"100-{task_directive['task_id']}"),
                        dict(mqid=f"200-{task_directive['task_id']}"),
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


@patch("wms.workflow_mq_activator.request_to_mqs", new_callable=AsyncMock)
@patch("wms.workflow_mq_activator.RestClient", new=MagicMock)  # it's a from-import
async def test_000(mock_req_to_mqs: AsyncMock) -> None:
    """Test the MQS scheduling with several tasks and requests."""
    mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")
    task_directives_client = database.client.WMSMongoClient(
        mongo_client,
        database.utils.TASK_DIRECTIVES_COLL_NAME,
    )
    taskforces_client = database.client.WMSMongoClient(
        mongo_client,
        database.utils.TASKFORCES_COLL_NAME,
    )

    # ingest data into mongo as if REST user did so
    for td_db in TEST_TASK_DIRECTIVES:
        await task_directives_client.insert_one(td_db)
        for i, location in enumerate(td_db["cluster_locations"]):  # type: ignore
            await taskforces_client.insert_one(_make_test_taskforce(td_db, location, i))

    # pre-patch all the REST calls to MQS
    mock_req_to_mqs.side_effect = MQSRESTCalls.request_to_mqs

    # go!
    with pytest.raises(asyncio.TimeoutError):
        # use asyncio's timeout to artificially stop loop, otherwise it'd go forever
        await asyncio.wait_for(workflow_mq_activator.startup(mongo_client), timeout=60)

    # check mongo db state
    tds_in_db = [t async for t in task_directives_client.find_all({}, [])]
    # look at task directives
    assert len(tds_in_db) == len(TEST_TASK_DIRECTIVES)
    # now, individually
    for td_db in tds_in_db:
        src = next(  # using 'next' gives shorter debug than w/ 'in'
            t for t in TEST_TASK_DIRECTIVES if t["task_id"] == td_db["task_id"]
        )
        # ignore the '_mqs_retry_at_ts' key, it's functionality is tested by MQSRESTCalls.request_to_mqs
        assert {k: v for k, v in td_db.items() if k != "_mqs_retry_at_ts"} == {
            **{k: v for k, v in src.items() if k != "_mqs_retry_at_ts"},
            "queues": [f"100-{td_db['task_id']}", f"200-{td_db['task_id']}"],
        }
        # look at taskforces
        tfs_in_db = [
            t
            async for t in taskforces_client.find_all(
                dict(task_id=td_db["task_id"]), []
            )
        ]
        assert tfs_in_db == [  # type: ignore
            _make_post_mqs_loop_taskforce(td_db, location, i)
            for i, location in enumerate(td_db["cluster_locations"])  # type: ignore
        ]
