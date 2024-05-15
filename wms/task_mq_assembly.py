"""The daemon task that 'assembles' message queues via the MQS."""

import asyncio
import logging
import time

import requests
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from rest_tools.client import ClientCredentialsAuth, RestClient

from . import database as db
from .config import ENV, MQS_RETRY_AT_TS_DEFAULT_VALUE, TASK_MQ_ASSEMBLY_SHORTEST_SLEEP
from .schema.enums import TaskforcePhase

LOGGER = logging.getLogger(__name__)


async def get_next_workflow(
    workflows_client: db.client.WMSMongoClient,
) -> dict:
    """Grab the next workflow from db."""
    return await workflows_client.find_one(
        {
            "queues": [],  # has no queues
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


async def request_to_mqs(mqs_rc: RestClient, workflow: dict) -> dict:
    """Send request to MQS for queues."""
    return await mqs_rc.request(
        "POST",
        "/mq-group",
        dict(
            workflow_id=workflow["workflow_id"],
            criteria=dict(
                priority=workflow["priority"],
                n_queues=len(workflow["queues"]),
            ),
        ),
    )


async def update_db(
    workflows_client: db.client.WMSMongoClient,
    task_directives_client: db.client.WMSMongoClient,
    taskforces_client: db.client.WMSMongoClient,
    workflow_id: str,
    queues: list[str],
) -> None:
    """Update the database with queues and advance taskforces' phases."""

    # update workflow -- insert queue ids
    # TODO - UPDATE QIDS
    await workflows_client.find_one_and_update(
        dict(workflow_id=workflow_id),
        dict(queues=queues),
    )
    LOGGER.info(f"ASSEMBLED {len(queues)} queues ({workflow_id=})")

    # get queues from task directive
    async for resp in task_directives_client.find_all(
        dict(workflow_id=workflow_id),
        projection=["task_id", "input_queue_aliases", "output_queue_aliases"],
    ):
        # update taskforces -- advance phase & insert queue ids
        environment_updates = {
            f"container_config.environment.EWMS_PILOT_QUEUE_INCOMING": ";".join(
                # map aliases to ids
                qinfo["id"]
                for qinfo in resp["input_queues"]
                if qinfo["alias"] in resp["input_queue_aliases"]
            ),
            f"container_config.environment.EWMS_PILOT_QUEUE_OUTGOING": ";".join(
                # map aliases to ids
                qinfo["id"]
                for qinfo in resp["output_queues"]
                if qinfo["alias"] in resp["output_queue_aliases"]
            ),
        }
        await taskforces_client.update_set_many(
            dict(task_id=resp["task_id"]),
            dict(
                phase=TaskforcePhase.PRE_LAUNCH,
                **environment_updates,
            ),
        )

    LOGGER.info(
        f"ADVANCED taskforces 'phase' TO {TaskforcePhase.PRE_LAUNCH} ({workflow_id=})"
    )


async def set_mqs_retry_at_ts(
    workflows_client: db.client.WMSMongoClient,
    workflow_id: str,
) -> None:
    """Set _mqs_retry_at_ts and place back on "backlog"."""
    retry_at = int(time.time()) + ENV.TASK_MQ_ASSEMBLY_MQS_RETRY_WAIT
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
    LOGGER.info("Starting up task_mq_assembly...")

    # database clients
    workflows_client = db.client.WMSMongoClient(
        mongo_client,
        db.utils.WORKFLOWS_COLL_NAME,
        parent_logger=LOGGER,
    )
    task_directives_client = db.client.WMSMongoClient(
        mongo_client,
        db.utils.TASK_DIRECTIVES_COLL_NAME,
        parent_logger=LOGGER,
    )
    taskforces_client = db.client.WMSMongoClient(
        mongo_client,
        db.utils.TASKFORCES_COLL_NAME,
        parent_logger=LOGGER,
    )

    # connect to mqs
    if ENV.CI:
        mqs_rc = RestClient(
            ENV.MQS_ADDRESS,
            logger=logging.getLogger(f"{LOGGER.name}.mqs"),
        )
    else:
        mqs_rc = ClientCredentialsAuth(
            ENV.MQS_ADDRESS,
            ENV.MQS_TOKEN_URL,
            ENV.MQS_CLIENT_ID,
            ENV.MQS_CLIENT_SECRET,
            logger=logging.getLogger(f"{LOGGER.name}.mqs"),
        )

    # main loop
    short_sleep = False
    while True:
        if short_sleep:
            await asyncio.sleep(TASK_MQ_ASSEMBLY_SHORTEST_SLEEP)
            short_sleep = False
        else:
            await asyncio.sleep(ENV.TASK_MQ_ASSEMBLY_DELAY)
        LOGGER.debug("Looking at next task directive without queues...")

        # find
        try:
            workflow = await get_next_workflow(workflows_client)
        except db.client.DocumentNotFoundException:
            LOGGER.debug("NOTHING FOR TASK_MQ_ASSEMBLY TO START UP")
            continue

        # request to mqs
        LOGGER.info(
            f"REQUESTING {len(workflow['queues'])} queues (workflow_id={workflow['workflow_id']})..."
        )
        try:
            resp = await request_to_mqs(mqs_rc, workflow)
        except requests.exceptions.HTTPError as e:
            LOGGER.exception(e)
            continue
        if resp.get("try_again_later"):
            await set_mqs_retry_at_ts(workflows_client, workflow["workflow_id"])
            short_sleep = True  # want to give other tasks a chance to start up
            continue

        # update db
        await update_db(
            workflows_client,
            task_directives_client,
            taskforces_client,
            workflow["workflow_id"],
            [p["mqid"] for p in resp["mqprofiles"]],
        )
