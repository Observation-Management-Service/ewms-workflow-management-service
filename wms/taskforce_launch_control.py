"""The daemon task that 'launches' pre-launch taskforces."""

import asyncio
import logging

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING

from . import database
from .config import ENV
from .schema.enums import TaskforcePhase

LOGGER = logging.getLogger(__name__)


async def startup(mongo_client: AsyncIOMotorClient) -> None:  # type: ignore[valid-type]
    """Start up the daemon task."""
    LOGGER.info("Starting up taskforce_launch_control...")

    wms_db = database.client.WMSMongoValidatedDatabase(
        mongo_client, parent_logger=LOGGER
    )

    while True:
        await asyncio.sleep(ENV.TASKFORCE_LAUNCH_CONTROL_DELAY)
        LOGGER.debug("Looking at next pre-launch taskforce...")

        # find & advance phase
        try:
            taskforce = await wms_db.taskforces_collection.find_one_and_update(
                dict(phase=TaskforcePhase.PRE_LAUNCH),
                dict(phase=TaskforcePhase.PENDING_STARTER),
                sort=[
                    ("worker_config.priority", DESCENDING),  # first, highest priority
                    ("timestamp", ASCENDING),  # then, oldest
                ],
            )
        except database.client.DocumentNotFoundException:
            LOGGER.debug("NOTHING FOR TASKFORCE_LAUNCH_CONTROL TO START UP")
        else:
            LOGGER.info(
                f"ADVANCED 'phase' FROM {TaskforcePhase.PRE_LAUNCH} TO {TaskforcePhase.PENDING_STARTER}"
                f" ({taskforce['taskforce_uuid']=})"
            )
