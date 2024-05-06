"""The daemon task that 'assembles' message queues via the MQS."""

import asyncio
import logging
import time

import requests
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from rest_tools.client import ClientCredentialsAuth, RestClient

from . import database as db
from .config import ENV, MQS_RETRY_AT_TS_DEFAULT_VALUE
from .schema.enums import TaskforcePhase

LOGGER = logging.getLogger(__name__)


async def set_mqs_retry_at_ts(
    task_directives_client: db.client.WMSMongoClient,
    task_id: str,
) -> None:
    """Set _mqs_retry_at_ts and place back on "backlog"."""
    retry_at = int(time.time()) + ENV.TASK_MQ_ASSEMBLY_MQS_RETRY_WAIT
    LOGGER.warning(
        f"MQS responded w/ 'not now' signal, will try task_directive "
        f"{task_id} at {retry_at} ({time.ctime(retry_at)})"
    )
    await task_directives_client.find_one_and_update(
        dict(task_id=task_id),
        dict(_mqs_retry_at_ts=retry_at),
    )


async def startup(mongo_client: AsyncIOMotorClient) -> None:  # type: ignore[valid-type]
    """Start up the daemon task."""
    LOGGER.info("Starting up task_mq_assembly...")

    # database clients
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
            await asyncio.sleep(1)
            short_sleep = False
        else:
            await asyncio.sleep(ENV.TASK_MQ_ASSEMBLY_DELAY)
        LOGGER.debug("Looking at next task directive without queues...")

        # find
        try:
            task_directive = await task_directives_client.find_one(
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
        except db.client.DocumentNotFoundException:
            LOGGER.debug("NOTHING FOR TASK_MQ_ASSEMBLY TO START UP")
            continue

        # request to mqs
        LOGGER.info(
            f"REQUESTING {task_directive['n_queues']} queues (task_id={task_directive['task_id']})..."
        )
        try:
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
        except requests.exceptions.HTTPError as e:
            LOGGER.exception(e)
            continue
        if resp.get("try_again_later"):
            await set_mqs_retry_at_ts(task_directives_client, task_directive["task_id"])
            short_sleep = True  # want to give other tasks a chance to start up
            continue

        queues = [p["mqid"] for p in resp["mqprofiles"]]

        # update task directive -- insert queues
        await task_directives_client.find_one_and_update(
            dict(task_id=task_directive["task_id"]),
            dict(queues=queues),
        )
        LOGGER.info(
            f"ASSEMBLED {len(resp['mqprofiles'])} queues (task_id={task_directive['task_id']})"
        )
        # update taskforces -- advance phase & insert queue ids
        environment_updates = {
            f"container_config.environment.EWMS_PILOT_QUEUE_{suffix}": qid
            for suffix, qid in zip(
                # TODO: add other types of queues (DEADLETTER, etc.)
                ["INCOMING", "OUTGOING"],
                queues,
            )
        }
        await taskforces_client.update_set_many(
            dict(task_id=task_directive["task_id"]),
            dict(
                phase=TaskforcePhase.PRE_LAUNCH,
                **environment_updates,
            ),
        )
        LOGGER.info(
            f"ADVANCED taskforces 'phase' TO {TaskforcePhase.PRE_LAUNCH} ({task_directive['task_id']}=)"
        )
