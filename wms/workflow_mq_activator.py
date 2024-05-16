"""The daemon task that 'assembles' message queues via the MQS."""

import asyncio
import logging
import time

import requests
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from rest_tools.client import RestClient

from . import database as db
from .config import ENV, MQS_RETRY_AT_TS_DEFAULT_VALUE, TASK_MQ_ASSEMBLY_SHORTEST_SLEEP
from .schema.enums import TaskforcePhase
from .utils import get_mqs_connection

LOGGER = logging.getLogger(__name__)


async def get_next_workflow(
    workflows_client: db.client.WMSMongoClient,
) -> dict:
    """Grab the next workflow from db."""
    return await workflows_client.find_one(
        {
            "mq_activated_ts": None,
            "$or": [
                # A: normal entries not needing a retry ('inf' indicates n/a)
                #    using 'inf' helps with sorting correctly, see 'sort' below
                {"_mqs_retry_at_ts": MQS_RETRY_AT_TS_DEFAULT_VALUE},
                # or B: any with an 'at time' that is due
                {"_mqs_retry_at_ts": {"$lte": int(time.time())}},
            ],
        },
        sort=[
            ("_mqs_retry_at_ts", ASCENDING),  # any w/ mqs-retry due (inf last)
            ("priority", DESCENDING),  # then, highest priority
            ("timestamp", ASCENDING),  # then, oldest
        ],
    )


async def request_activation_to_mqs(mqs_rc: RestClient, workflow: dict) -> dict:
    """Send request to MQS to activate workflow's queues."""
    return await mqs_rc.request(
        "POST",
        "/mq-group/activate",
        dict(
            workflow_id=workflow["workflow_id"],
            criteria=dict(
                priority=workflow["priority"],
                # TODO (future PR) - add other fields
            ),
        ),
    )


async def advance_taskforce_phases(
    taskforces_client: db.client.WMSMongoClient,
    workflow_id: str,
) -> None:
    """Update the database taskforces' phases with TaskforcePhase.PRE_LAUNCH."""
    await taskforces_client.update_set_many(
        dict(workflow_id=workflow_id),
        dict(phase=TaskforcePhase.PRE_LAUNCH),
    )

    LOGGER.info(
        f"ADVANCED taskforces 'phase' TO {TaskforcePhase.PRE_LAUNCH} ({workflow_id=})"
    )


async def set_mq_activated_ts(
    workflows_client: db.client.WMSMongoClient,
    workflow_id: str,
) -> None:
    """Set mq_activated_ts in db."""
    await workflows_client.find_one_and_update(
        dict(workflow_id=workflow_id),
        dict(mq_activated_ts=int(time.time())),
    )


async def set_mqs_retry_at_ts(
    workflows_client: db.client.WMSMongoClient,
    workflow_id: str,
) -> None:
    """Set _mqs_retry_at_ts and place back on "backlog"."""
    retry_at = time.time() + ENV.TASK_MQ_ASSEMBLY_MQS_RETRY_WAIT
    LOGGER.warning(
        f"MQS responded w/ 'not now' signal, will try workflow "
        f"{workflow_id} after {retry_at} ({time.ctime(retry_at)})"
    )
    await workflows_client.find_one_and_update(
        dict(workflow_id=workflow_id),
        dict(_mqs_retry_at_ts=retry_at),
    )


async def startup(mongo_client: AsyncIOMotorClient) -> None:  # type: ignore[valid-type]
    """Start up the daemon task."""
    LOGGER.info("Starting up workflow_mq_activator...")

    # database clients
    workflows_client = db.client.WMSMongoClient(
        mongo_client,
        db.utils.WORKFLOWS_COLL_NAME,
        parent_logger=LOGGER,
    )
    taskforces_client = db.client.WMSMongoClient(
        mongo_client,
        db.utils.TASKFORCES_COLL_NAME,
        parent_logger=LOGGER,
    )
    # rest client
    mqs_rc = get_mqs_connection(logging.getLogger(f"{LOGGER.name}.mqs"))

    # main loop
    short_sleep = False
    while True:
        if short_sleep:
            await asyncio.sleep(TASK_MQ_ASSEMBLY_SHORTEST_SLEEP)
            short_sleep = False
        else:
            await asyncio.sleep(ENV.WORKFLOW_MQ_ACTIVATOR_DELAY)
        LOGGER.debug("Looking at next task directive without queues...")

        # find
        try:
            workflow = await get_next_workflow(workflows_client)
        except db.client.DocumentNotFoundException:
            LOGGER.debug("NOTHING FOR TASK_MQ_ASSEMBLY TO START UP")
            continue

        # request to mqs
        LOGGER.info(
            f"REQUESTING ACTIVATION for {len(workflow['queues'])} queues (workflow_id={workflow['workflow_id']})..."
        )
        try:
            resp = await request_activation_to_mqs(mqs_rc, workflow)
        except requests.exceptions.HTTPError as e:
            LOGGER.exception(e)
            continue
        # update db workflow w/ result
        if resp.get("try_again_later"):
            await set_mqs_retry_at_ts(workflows_client, workflow["workflow_id"])
            short_sleep = True  # want to give other tasks a chance to start up
            continue
        else:
            await set_mq_activated_ts(workflows_client, workflow["workflow_id"])

        LOGGER.info(
            f"ACTIVATED {len(resp['mqprofiles'])} queues (workflow_id={workflow['workflow_id']})"
        )

        # update db -- taskforces
        await advance_taskforce_phases(taskforces_client, workflow["workflow_id"])
