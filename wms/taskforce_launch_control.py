"""The daemon task that 'launches' pre-launch taskforces."""


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
    LOGGER.info("Starting up taskforce_launch_control...")

    taskforces_client = db.client.WMSMongoClient(
        mongo_client,
        db.utils.TASKFORCES_COLL_NAME,
    )

    while True:
        LOGGER.info("Looking at next pre-launch taskforce...")

        # find & advance phase
        try:
            taskforce = await taskforces_client.find_one_and_update(
                dict(phase=TaskforcePhase.PRE_LAUNCH),
                dict(phase=TaskforcePhase.PENDING_STARTER),
                sort=[
                    ("worker_config.priority", DESCENDING),  # first, highest priority
                    ("timestamp", ASCENDING),  # then, oldest
                ],
            )
        except db.client.DocumentNotFoundException:
            LOGGER.info("NOTHING FOR TASKFORCE_LAUNCH_CONTROL TO START UP")
            await asyncio.sleep(ENV.TASKFORCE_LAUNCH_CONTROL_SHORT_DELAY)
        else:
            LOGGER.info(
                f"ADVANCED 'phase' FROM {TaskforcePhase.PRE_LAUNCH} TO {TaskforcePhase.PENDING_STARTER}"
                f" ({taskforce['taskforce_uuid']=})"
            )
            await asyncio.sleep(ENV.TASKFORCE_LAUNCH_CONTROL_DELAY)
