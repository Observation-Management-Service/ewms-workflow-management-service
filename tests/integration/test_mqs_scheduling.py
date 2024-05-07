"""Test the MQS scheduling logic with the task_mq_assembly module/daemon.

Runs everything in main process and thread. Uses a real mongo database
and mock/patched MQS REST calls."""

import asyncio

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from wms import task_mq_assembly, database, config, schema

TEST_TASK_DIRECTIVES = [
    dict(
        task_id="123",
        cluster_locations=["foo", "bar"],
        task_image="bap",
        task_args="--baz bat",
        timestamp=1,
        priority=10,
        #
        n_queues=2,
        queues=[],
        _mqs_retry_at_ts=config.MQS_RETRY_AT_TS_DEFAULT_VALUE,
        #
        aborted=False,
    ),
]


def _make_test_taskforce(task_directive: dict, location: str, i: int) -> dict:
    return dict(
        tuaskforce_uuid=f"{task_directive['task_id']}-{i}",
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


async def test_000() -> None:
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

    # TODO: pre-patch all the rest calls to MQS

    with pytest.raises(asyncio.TimeoutError):
        # use asyncio's timeout to artificially stop loop, otherwise it'd go forever
        await asyncio.wait_for(task_mq_assembly.startup(mongo_client), timeout=60)

    # TODO: check calls and mongo db state
