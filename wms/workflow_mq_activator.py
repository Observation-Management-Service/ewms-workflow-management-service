"""The daemon task that activates message queues via the MQS."""

import asyncio
import logging
import time
from typing import Any

import motor
import requests
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from rest_tools.client import RestClient

from . import database
from .config import ENV, MQS_RETRY_AT_TS_DEFAULT_VALUE, TASK_MQ_ACTIVATOR_SHORTEST_SLEEP
from .schema.enums import TaskforcePhase
from .utils import get_mqs_connection

LOGGER = logging.getLogger(__name__)


async def get_next_workflow(
    workflows_client: database.client.MongoValidatedCollection,
) -> dict:
    """Grab the next workflow from db."""
    return await workflows_client.find_one(
        {
            "mq_activated_ts": None,
            "$or": [
                # A: normal entries not needing a retry ('inf' indicates n/a)
                #    using 'inf' helps with sorting correctly, see 'sort' below
                {"_mq_activation_retry_at_ts": MQS_RETRY_AT_TS_DEFAULT_VALUE},
                # or B: any with an 'at time' that is due
                {"_mq_activation_retry_at_ts": {"$lte": time.time()}},
            ],
        },
        sort=[
            (
                "_mq_activation_retry_at_ts",
                ASCENDING,
            ),  # any w/ mqs-retry due (inf last)
            ("priority", DESCENDING),  # then, highest priority
            ("timestamp", ASCENDING),  # then, oldest
        ],
    )


async def request_activation_to_mqs(mqs_rc: RestClient, workflow: dict) -> dict:
    """Send request to MQS to activate workflow's queues."""
    return await mqs_rc.request(
        "POST",
        f"/v0/mqs/workflows/{workflow['workflow_id']}/mq-group/activation",
        {
            "workflow_id": workflow["workflow_id"],
            "criteria": {
                "priority": workflow["priority"],
                # TODO (future PR) - add other fields
            },
        },
    )


async def _update_taskforces_w_mqprofile_info(
    wms_db: database.client.WMSMongoValidatedDatabase,
    workflow_id: str,
    mqprofile: dict[str, Any],
    session: motor.motor_asyncio.AsyncIOMotorClientSession,
) -> None:
    """Update all the taskforces with a queue (input or output) matching the mqprofile."""
    LOGGER.debug(f"Updating taskforces for {workflow_id=} {mqprofile['mqid']=}")
    mqid = mqprofile["mqid"]
    auth_token = mqprofile["auth_token"]
    broker_type = mqprofile["broker_type"]
    broker_address = mqprofile["broker_address"]

    # input/incoming
    async for td in wms_db.task_directives_collection.find_all(
        {
            "workflow_id": workflow_id,
            "input_queues": mqprofile["mqid"],  # mongo-speak for "is entry X in list?"
        },
        [],
    ):
        await wms_db.taskforces_collection.update_many(
            {
                "workflow_id": workflow_id,
                "task_id": td["task_id"],
            },
            {
                "$push": {  # mongo appends to list
                    "pilot_config.environment.EWMS_PILOT_QUEUE_INCOMING": mqid,
                    "pilot_config.environment.EWMS_PILOT_QUEUE_INCOMING_AUTH_TOKEN": auth_token,
                    "pilot_config.environment.EWMS_PILOT_QUEUE_INCOMING_BROKER_TYPE": broker_type,
                    "pilot_config.environment.EWMS_PILOT_QUEUE_INCOMING_BROKER_ADDRESS": broker_address,
                }
            },
            session=session,
        )

    # output/outgoing (same as above but for outgoing queues)
    async for td in wms_db.task_directives_collection.find_all(
        {
            "workflow_id": workflow_id,
            "output_queues": mqprofile["mqid"],  # mongo-speak for "is entry X in list?"
        },
        [],
    ):
        await wms_db.taskforces_collection.update_many(
            {
                "workflow_id": workflow_id,
                "task_id": td["task_id"],
            },
            {
                "$push": {  # mongo appends to list
                    "pilot_config.environment.EWMS_PILOT_QUEUE_OUTGOING": mqid,
                    "pilot_config.environment.EWMS_PILOT_QUEUE_OUTGOING_AUTH_TOKEN": auth_token,
                    "pilot_config.environment.EWMS_PILOT_QUEUE_OUTGOING_BROKER_TYPE": broker_type,
                    "pilot_config.environment.EWMS_PILOT_QUEUE_OUTGOING_BROKER_ADDRESS": broker_address,
                }
            },
            session=session,
        )


async def advance_database(
    wms_db: database.client.WMSMongoValidatedDatabase,
    workflow_id: str,
    mqprofiles: list[dict[str, Any]],
) -> None:
    """Update the database with info regarding queues.

    1. mq_activated_ts
    2. taskforces' phases with TaskforcePhase.PRE_LAUNCH
    3. add queue ids and auth tokens to taskforces' env vars
    """
    async with await wms_db.mongo_client.start_session() as s:
        async with s.start_transaction():
            # set mq_activated_ts
            await wms_db.workflows_collection.find_one_and_update(
                {"workflow_id": workflow_id},
                {"$set": {"mq_activated_ts": time.time()}},
                session=s,
            )
            # match mqprofiles with taskforces (N:M)
            for mqprofile in mqprofiles:
                await _update_taskforces_w_mqprofile_info(
                    wms_db,
                    workflow_id,
                    mqprofile,
                    session=s,
                )
            # update phase
            await wms_db.taskforces_collection.update_many(
                {
                    "workflow_id": workflow_id,
                },
                {
                    "$set": {
                        "phase": TaskforcePhase.PRE_LAUNCH,
                    },
                    "$push": {
                        "phase_change_log": {
                            "target_phase": TaskforcePhase.PRE_LAUNCH,
                            "timestamp": time.time(),
                            "was_successful": True,
                            "source_event_time": None,
                            "source_entity": "Workflow MQ Activator",
                            "description": "",
                        },
                    },
                },
                session=s,
            )

    LOGGER.info(f"ACTIVATED queues for workflow_id={workflow_id}")
    LOGGER.info(
        f"ADVANCED taskforces 'phase' TO {TaskforcePhase.PRE_LAUNCH} ({workflow_id=})"
    )


async def set_mq_activation_retry_at_ts(
    workflows_client: database.client.MongoValidatedCollection,
    workflow_id: str,
) -> None:
    """Set _mq_activation_retry_at_ts and place back on "backlog"."""
    retry_at = time.time() + ENV.WORKFLOW_MQ_ACTIVATOR_MQS_RETRY_WAIT
    LOGGER.warning(
        f"MQS responded w/ 'not now' signal, will try workflow "
        f"{workflow_id} after {retry_at} ({time.ctime(retry_at)})"
    )
    await workflows_client.find_one_and_update(
        {
            "workflow_id": workflow_id,
        },
        {
            "$set": {"_mq_activation_retry_at_ts": retry_at},
        },
    )


async def run(mongo_client: AsyncIOMotorClient) -> None:  # type: ignore[valid-type]
    """Start up the daemon task."""
    LOGGER.info("Starting up workflow_mq_activator...")

    # database client
    wms_db = database.client.WMSMongoValidatedDatabase(
        mongo_client, parent_logger=LOGGER
    )
    # rest client
    mqs_rc = get_mqs_connection(logging.getLogger(f"{LOGGER.name}.mqs"))

    # main loop
    short_sleep = False
    while True:
        if short_sleep:
            await asyncio.sleep(TASK_MQ_ACTIVATOR_SHORTEST_SLEEP)
            short_sleep = False
        else:
            await asyncio.sleep(ENV.WORKFLOW_MQ_ACTIVATOR_DELAY)
        LOGGER.debug("Looking at next task directive without queues...")

        # find
        try:
            workflow = await get_next_workflow(wms_db.workflows_collection)
        except database.client.DocumentNotFoundException:
            LOGGER.debug("NOTHING FOR TASK_MQ_ACTIVATOR TO START UP")
            continue

        # request to mqs
        LOGGER.info(
            f"REQUESTING ACTIVATION for workflow_id={workflow['workflow_id']} queues..."
        )
        try:
            mqs_resp = await request_activation_to_mqs(mqs_rc, workflow)
        except requests.exceptions.HTTPError as e:
            LOGGER.exception(e)
            continue
        # update database per result
        if mqs_resp.get("try_again_later"):
            await set_mq_activation_retry_at_ts(
                wms_db.workflows_collection,
                workflow["workflow_id"],
            )
            short_sleep = True  # want to give other tasks a chance to start up
            continue
        else:
            await advance_database(
                wms_db,
                workflow["workflow_id"],
                mqs_resp["mqprofiles"],
            )
