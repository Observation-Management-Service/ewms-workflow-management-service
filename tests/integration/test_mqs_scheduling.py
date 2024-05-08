"""Test the MQS scheduling logic with the task_mq_assembly module/daemon.

Runs everything in main process and thread. Uses a real mongo database
and mock/patched MQS REST calls."""

import asyncio
import logging
import time
from typing import Any
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from wms import task_mq_assembly, database, config, schema

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
                        dict(mqid=f"100-{MQSRESTCalls.call_ct}"),
                        dict(mqid=f"200-{MQSRESTCalls.call_ct}"),
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
                        dict(mqid=f"100-{MQSRESTCalls.call_ct}"),
                        dict(mqid=f"200-{MQSRESTCalls.call_ct}"),
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
                        dict(mqid=f"100-{MQSRESTCalls.call_ct}"),
                        dict(mqid=f"200-{MQSRESTCalls.call_ct}"),
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
                    <= MQSRESTCalls.retry_dues[task_directive["task_id"]] + 1
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
                    <= MQSRESTCalls.retry_dues[task_directive["task_id"]] + 1
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
                    <= MQSRESTCalls.retry_dues[task_directive["task_id"]] + 1
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
                    <= MQSRESTCalls.retry_dues[task_directive["task_id"]] + 1
                )
                return dict(
                    mqprofiles=[
                        dict(mqid=f"100-{MQSRESTCalls.call_ct}"),
                        dict(mqid=f"200-{MQSRESTCalls.call_ct}"),
                    ]
                )
            # retry: re-deny B
            case 9:
                assert task_directive["task_id"] == "B2"
                assert (
                    MQSRESTCalls.retry_dues[task_directive["task_id"]]
                    <= time.time()
                    <= MQSRESTCalls.retry_dues[task_directive["task_id"]] + 1
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
                    <= MQSRESTCalls.retry_dues[task_directive["task_id"]] + 1
                )
                return dict(
                    mqprofiles=[
                        dict(mqid=f"100-{MQSRESTCalls.call_ct}"),
                        dict(mqid=f"200-{MQSRESTCalls.call_ct}"),
                    ]
                )
            # ???
            case other:
                print(other)
                assert 0


@patch("wms.task_mq_assembly.request_to_mqs", new_callable=AsyncMock)
@patch("wms.task_mq_assembly.RestClient", new=MagicMock)  # it's a from-import
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
    for task_directive in TEST_TASK_DIRECTIVES:
        await task_directives_client.insert_one(task_directive)
        for i, location in enumerate(task_directive["cluster_locations"]):  # type: ignore
            await taskforces_client.insert_one(
                _make_test_taskforce(task_directive, location, i)
            )

    # pre-patch all the REST calls to MQS
    mock_req_to_mqs.side_effect = MQSRESTCalls.request_to_mqs

    # go!
    with pytest.raises(asyncio.TimeoutError):
        # use asyncio's timeout to artificially stop loop, otherwise it'd go forever
        await asyncio.wait_for(task_mq_assembly.startup(mongo_client), timeout=60)

    # TODO: check mongo db state
