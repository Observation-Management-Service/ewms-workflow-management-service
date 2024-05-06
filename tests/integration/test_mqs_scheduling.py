"""Test the MQS scheduling logic with the task_mq_assembly module/daemon.

Runs everything in main process and thread. Uses a real mongo database
and mock/patched MQS REST calls."""

import asyncio

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from wms import task_mq_assembly


async def test_000() -> None:
    """Test the MQS scheduling with several tasks and requests."""
    mongo = AsyncIOMotorClient("mongodb://localhost:27017")

    # TODO: ingest data into mongo as if user did so

    # TODO: pre-patch all the rest calls to MQS

    with pytest.raises(asyncio.TimeoutError):
        # use asyncio's timeout to artificially stop loop, otherwise it'd go forever
        await asyncio.wait_for(task_mq_assembly.startup(mongo), timeout=60)

    # TODO: check calls and mongo db state
