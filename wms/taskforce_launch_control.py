"""The daemon task that 'launches' pre-launch taskforces."""

import asyncio
import logging
import time

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING

from . import database
from .config import ENV
from .schema.enums import TaskforcePhase
from .utils import resilient_daemon_task

LOGGER = logging.getLogger(__name__)


@resilient_daemon_task(ENV.TASKFORCE_LAUNCH_CONTROL_DELAY, LOGGER)
async def run(mongo_client: AsyncIOMotorClient) -> None:  # type: ignore[valid-type]
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
                {
                    "phase": TaskforcePhase.PRE_LAUNCH,
                },
                {
                    "$set": {
                        "phase": TaskforcePhase.PENDING_STARTER,
                    },
                    "$push": {
                        "phase_change_log": {
                            "target_phase": TaskforcePhase.PENDING_STARTER,
                            "timestamp": time.time(),
                            "was_successful": True,
                            "source_event_time": None,
                            "source_entity": "Taskforce Launch Control",
                            "context": "",
                        },
                    },
                },
                sort=[
                    ("priority", DESCENDING),  # first, highest priority
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
