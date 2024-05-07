"""Test the MQS scheduling logic with the task_mq_assembly module/daemon.

Runs everything in main process and thread. Uses a real mongo database
and mock/patched MQS REST calls."""

import asyncio
from unittest.mock import patch, MagicMock

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from wms import task_mq_assembly, database, config, schema

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
        worker_config={},
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

    @staticmethod
    def request(method: str, path: str, body: dict) -> dict:
        assert method == "POST"
        assert path == "/mq-group"
        MQSRESTCalls.call_ct += 1
        match MQSRESTCalls.call_ct:
            # accept A
            case 0:
                assert body["task_id"] == "A1"
                return dict(
                    mqprofiles=[
                        dict(mqid=f"100-{MQSRESTCalls.call_ct}"),
                        dict(mqid=f"200-{MQSRESTCalls.call_ct}"),
                    ]
                )
            # deny B
            case 1:
                assert body["task_id"] == "B2"
                return dict(try_again_later=True)
            # accept C
            case 2:
                assert body["task_id"] == "C3"
                dict(
                    mqprofiles=[
                        dict(mqid=f"100-{MQSRESTCalls.call_ct}"),
                        dict(mqid=f"200-{MQSRESTCalls.call_ct}"),
                    ]
                )
            # accept D
            case 3:
                assert body["task_id"] == "D4"
                dict(
                    mqprofiles=[
                        dict(mqid=f"100-{MQSRESTCalls.call_ct}"),
                        dict(mqid=f"200-{MQSRESTCalls.call_ct}"),
                    ]
                )
            # deny E
            case 4:
                assert body["task_id"] == "E5"
                return dict(try_again_later=True)
            # deny B
            case 5:
                assert body["task_id"] == "B2"
                return dict(try_again_later=True)
            # deny E
            case 6:
                assert body["task_id"] == "E5"
                return dict(try_again_later=True)
            # deny B
            case 7:
                assert body["task_id"] == "B2"
                return dict(try_again_later=True)
            # accept E
            case 8:
                assert body["task_id"] == "E5"
                dict(
                    mqprofiles=[
                        dict(mqid=f"100-{MQSRESTCalls.call_ct}"),
                        dict(mqid=f"200-{MQSRESTCalls.call_ct}"),
                    ]
                )
            # deny B
            case 9:
                assert body["task_id"] == "B2"
                return dict(try_again_later=True)
            # accept B
            case 10:
                assert body["task_id"] == "B2"
                dict(
                    mqprofiles=[
                        dict(mqid=f"100-{MQSRESTCalls.call_ct}"),
                        dict(mqid=f"200-{MQSRESTCalls.call_ct}"),
                    ]
                )
            # ???
            case other:
                print(other)
                assert 0
        assert 0


@patch("rest_tools.client.RestClient")
async def test_000(mock_mqs_rc: MagicMock) -> None:
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
    mock_mqs_rc.request.side_effect = MQSRESTCalls.request

    # go!
    with pytest.raises(asyncio.TimeoutError):
        # use asyncio's timeout to artificially stop loop, otherwise it'd go forever
        await asyncio.wait_for(task_mq_assembly.startup(mongo_client), timeout=60)

    # TODO: check mongo db state
