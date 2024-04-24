"""The daemon task that serves the backlog."""


import asyncio
import logging

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING

from . import database as db
from .config import ENV
from .schema.enums import TaskforcePhase

LOGGER = logging.getLogger(__name__)


async def startup(mongo_client: AsyncIOMotorClient) -> None:  # type: ignore[valid-type]
    """Start up the daemon task."""
    LOGGER.info("Starting up backlogger...")

    taskforces_client = db.client.WMSMongoClient(
        mongo_client,
        db.utils.TASKFORCES_COLL_NAME,
    )

    while True:
        LOGGER.info("Looking at next in backlog...")

        try:
            await taskforces_client.find_one_and_update(
                dict(phase=TaskforcePhase.PRE_LAUNCH),
                dict(phase=TaskforcePhase.PENDING_STARTER),
                sort=[
                    ("worker_config.priority", DESCENDING),  # highest first
                    ("timestamp", ASCENDING),  # oldest first
                ],
            )
        except db.client.DocumentNotFoundException:
            LOGGER.info("NOTHING IN BACKLOG TO START UP")
            await asyncio.sleep(ENV.BACKLOG_RUNNER_SHORT_DELAY)
        else:
            LOGGER.info(
                f"CHANGED 'phase' FROM {TaskforcePhase.PRE_LAUNCH} TO {TaskforcePhase.PENDING_STARTER}"
            )
            await asyncio.sleep(ENV.BACKLOG_RUNNER_DELAY)
