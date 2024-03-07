"""The daemon task that serves the backlog."""


import asyncio
import logging

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING

from . import database as db
from .config import ENV

LOGGER = logging.getLogger(__name__)


async def startup(mongo_client: AsyncIOMotorClient) -> None:  # type: ignore[valid-type]
    """Start up the daemon task."""
    taskforces_client = db.client.WMSMongoClient(
        mongo_client,
        db.utils.TASKFORCES_COLL_NAME,
    )

    while True:
        modified_count = await taskforces_client.update_set_one(
            dict(tms_most_recent_action="pre-tms"),
            dict(tms_most_recent_action="pending-starter"),
            sort=[
                ("worker_config.priority", DESCENDING),  # highest first
                ("timestamp", ASCENDING),  # oldest first
            ],
        )

        if not modified_count:
            await asyncio.sleep(ENV.BACKLOG_RUNNER_SHORT_DELAY)
        else:
            await asyncio.sleep(ENV.BACKLOG_RUNNER_DELAY)
