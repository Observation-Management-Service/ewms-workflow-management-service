"""The daemon task that 'assembles' message queues via the MQS."""


import asyncio
import logging

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from rest_tools.client import RestClient

from . import database as db
from .config import ENV
from .schema.enums import TaskforcePhase

LOGGER = logging.getLogger(__name__)


async def startup(mongo_client: AsyncIOMotorClient) -> None:  # type: ignore[valid-type]
    """Start up the daemon task."""
    LOGGER.info("Starting up task_mq_assembly...")

    task_directives_client = db.client.WMSMongoClient(
        mongo_client,
        db.utils.TASK_DIRECTIVES_COLL_NAME,
    )
    taskforces_client = db.client.WMSMongoClient(
        mongo_client,
        db.utils.TASKFORCES_COLL_NAME,
    )
    mqs_rc = RestClient(
        ENV.MQS_ADDRESS,
        logger=logging.getLogger(f"{LOGGER.name}.mqs"),
    )

    while True:
        LOGGER.info("Looking at next task directive without queues...")

        # find
        try:
            task_directive = await task_directives_client.find_one(
                dict(queues=[]),  # has no queues
                sort=[
                    ("priority", DESCENDING),  # first, highest priority
                    ("timestamp", ASCENDING),  # then, oldest
                ],
            )
        except db.client.DocumentNotFoundException:
            LOGGER.info("NOTHING FOR TASK_MQ_ASSEMBLY TO START UP")
            await asyncio.sleep(ENV.TASK_MQ_ASSEMBLY_SHORT_DELAY)
            continue

        # request to mqs
        LOGGER.info(
            f"REQUESTING {task_directive['n_queues']} queues (task_id={task_directive['task_id']})..."
        )
        resp = await mqs_rc.request(
            "POST",
            "/mq-group",
            dict(
                criteria=dict(
                    priority=task_directive["priority"],
                    n_queues=task_directive["n_queues"],
                )
            ),
        )
        # TODO - Add error handling ^^^

        # update task directive -- insert queues
        await task_directives_client.find_one_and_update(
            dict(task_id=task_directive["task_id"]),
            dict(queues=[p["mqid"] for p in resp["mqprofiles"]]),
        )
        LOGGER.info(
            f"ASSEMBLED {len(resp['mqprofiles'])} queues (task_id={task_directive['task_id']})"
        )
        # update taskforces -- advance phase
        await taskforces_client.update_set_many(
            dict(task_id=task_directive["task_id"]),
            dict(phase=TaskforcePhase.PRE_LAUNCH),
        )
        LOGGER.info(
            f"ADVANCED taskforces 'phase' TO {TaskforcePhase.PRE_LAUNCH} ({task_directive['task_id']}=)"
        )

        await asyncio.sleep(ENV.TASK_MQ_ASSEMBLY_DELAY)
