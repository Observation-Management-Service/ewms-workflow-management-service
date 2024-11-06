"""The daemon task that activates message queues via the MQS."""

import asyncio
import logging
import time

import requests
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from rest_tools.client import RestClient

from . import database
from .config import ENV, MQS_RETRY_AT_TS_DEFAULT_VALUE, TASK_MQ_ACTIVATOR_SHORTEST_SLEEP
from .database.client import DocumentNotFoundException
from .schema.enums import TaskforcePhase
from .utils import get_mqs_connection

LOGGER = logging.getLogger(__name__)

PCL_SOURCE_ENTITY = "Workflow MQ Activator"


class NoWorkflowToMQActivate(Exception):
    """Raised when there is not a workflow object to activate."""


def _mongo_syntax_advance_taskforce_to_prelaunch(context: str = "") -> dict:
    return {
        "$set": {
            "phase": TaskforcePhase.PRE_LAUNCH,
        },
        "$push": {  # Append an entry to the phase_change_log
            "phase_change_log": {
                "target_phase": TaskforcePhase.PRE_LAUNCH,
                "timestamp": time.time(),
                "was_successful": True,
                "source_event_time": None,
                "source_entity": PCL_SOURCE_ENTITY,
                "context": context,
            }
        },
    }


async def get_next_workflow_id(
    wms_db: database.client.WMSMongoValidatedDatabase,
) -> str:
    """Grab the id of the next workflow from db.

    Find the next taskforce in the "pre-mq-activation" phase, then get its workflow id.
    That way, we can activate all its sibling (and cousin) taskforces together.

    It checks if this taskforce is behind its sibling taskforces
    (those sharing the same `workflow_id`) by verifying if any sibling has already progressed
    to a later phase. If the taskforce is behind, it automatically advances the phase to "pre-launch"
    and logs this phase change. If it is not behind, it returns the `workflow_id` of the taskforce.
    """
    while True:
        # Aggregation pipeline to find the taskforce and check if it is behind
        pipeline = [
            # Stage 1: Match documents in the "pre-mq-activation" phase and with specific phase change conditions
            {
                "$match": {
                    "phase": "pre-mq-activation",
                    "$or": [
                        {
                            # Case 1: Taskforce has no failed attempts to transition to "pre-mq-activation"
                            "phase_change_log": {
                                "$not": {
                                    "$elemMatch": {
                                        "target_phase": TaskforcePhase.PRE_MQ_ACTIVATOR,
                                        "was_successful": False,
                                    }
                                }
                            }
                        },
                        {
                            # Case 2: Taskforce has a failed attempt, but it was at least `X` seconds ago
                            "phase_change_log": {
                                "$elemMatch": {
                                    "target_phase": TaskforcePhase.PRE_MQ_ACTIVATOR,
                                    "was_successful": False,
                                    "timestamp": {
                                        "$lte": time.time()
                                        - MQS_RETRY_AT_TS_DEFAULT_VALUE
                                    },
                                }
                            }
                        },
                    ],
                }
            },
            # Stage 2: Sort
            {
                "$sort": {
                    "priority": DESCENDING,  # first, by `priority` (highest first)
                    "timestamp": ASCENDING,  # then, by `timestamp` (oldest first)
                }
            },
            # Stage 3: Limit to the first top-matching document
            {"$limit": 1},
            # Stage 4: Lookup sibling taskforces that are in later phases
            {
                "$lookup": {
                    "from": wms_db.taskforces_collection.collection_name,  # The same collection for "self-join" to find siblings
                    "let": {
                        "workflow_id": "$workflow_id",  # Pass `workflow_id` of current taskforce
                    },
                    "pipeline": [
                        {
                            "$match": {
                                # Match taskforces with the same `workflow_id` and later phase
                                "$expr": {
                                    "$and": [
                                        # fmt: off
                                        {"$eq": ["$workflow_id", "$$workflow_id"]},
                                        {"$ne": ["$phase", TaskforcePhase.PRE_MQ_ACTIVATOR]},
                                        # fmt: on
                                    ]
                                }
                            }
                        }
                    ],
                    "as": "later_phase_siblings",  # Field to store siblings found in later phases
                }
            },
            # Stage 5: Project only necessary fields and determine if the taskforce is behind
            {
                "$project": {
                    "taskforce_uuid": 1,
                    "workflow_id": 1,
                    "timestamp": 1,
                    "phase": 1,
                    "workflow_already_mq_activated": {  # `True` if there are any later-phase siblings
                        "$gt": [{"$size": "$later_phase_siblings"}, 0]
                    },
                }
            },
        ]

        async with await wms_db.mongo_client.start_session() as s:
            async with s.start_transaction():  # atomic
                # Execute the aggregation pipeline
                try:
                    result = await wms_db.taskforces_collection.aggregate_one(pipeline, session=s)  # type: ignore
                except DocumentNotFoundException:
                    raise NoWorkflowToMQActivate()

                LOGGER.info(f"mq-activation search: found taskforce {result}")

                # IF not behind, return the workflow_id
                if not result["workflow_already_mq_activated"]:
                    return result["workflow_id"]
                # ELSE, update its phase to "pre-launch" if needed--then loop
                else:
                    LOGGER.info(
                        f"Advancing taskforce {result["taskforce_uuid"]} because "
                        f"its workflow (aka its sibling taskforces) has already been mq-activated..."
                    )
                    await wms_db.taskforces_collection.find_one_and_update(
                        {"taskforce_uuid": result["taskforce_uuid"]},
                        _mongo_syntax_advance_taskforce_to_prelaunch(
                            context="Auto-advanced because workflow has already been mq-activated."
                        ),
                        session=s,
                    )
        # fall-through -- look again
        LOGGER.info("Looking again for the next workflow to mq-activate...")


async def request_activation_to_mqs(
    workflows_client: database.client.MongoValidatedCollection,
    mqs_rc: RestClient,
    workflow_id: str,
) -> dict:
    """Send request to MQS to activate workflow's queues."""
    workflow = await workflows_client.find_one({"workflow_id": workflow_id})

    return await mqs_rc.request(
        "POST",
        f"/v0/mqs/workflows/{workflow['workflow_id']}/mq-group/activation",
        {
            "workflow_id": workflow["workflow_id"],  # could also use param arg
            "criteria": {
                "priority": workflow["priority"],
                # TODO (future PR) - add other fields
            },
        },
    )


async def advance_workflows_taskforces_to_prelaunch(
    taskforces_client: database.client.MongoValidatedCollection,
    workflow_id: str,
) -> None:
    """Advance taskforces' phases to TaskforcePhase.PRE_LAUNCH."""
    await taskforces_client.update_many(
        {"workflow_id": workflow_id},
        _mongo_syntax_advance_taskforce_to_prelaunch(),
    )
    LOGGER.info(
        f"ADVANCED taskforces 'phase' TO {TaskforcePhase.PRE_LAUNCH} ({workflow_id=})"
    )


async def record_mq_activation_failed(
    taskforces_client: database.client.MongoValidatedCollection,
    workflow_id: str,
    reason: str,
) -> None:
    """Record that mq-activation failed and "place workflow back on backlog"."""
    retry_at = time.time() + ENV.WORKFLOW_MQ_ACTIVATOR_MQS_RETRY_WAIT
    LOGGER.warning(
        f"MQ-ACTIVATION FAILED: {reason} -- will retry workflow "
        f"{workflow_id} after {retry_at} ({time.ctime(retry_at)})"
    )
    await taskforces_client.update_many(
        {
            "workflow_id": workflow_id,
        },
        {
            # no "$set" needed, the phase is not changing
            "$push": {
                "phase_change_log": {
                    "target_phase": TaskforcePhase.PRE_LAUNCH,
                    "timestamp": time.time(),
                    "was_successful": False,  # it failed!
                    "source_event_time": None,
                    "source_entity": PCL_SOURCE_ENTITY,
                    "context": reason,
                },
            },
        },
    )


########################################################################################


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
        LOGGER.debug("Looking at workflow to mq-activate...")

        # find next
        try:
            workflow_id = await get_next_workflow_id(wms_db)
        except NoWorkflowToMQActivate:
            LOGGER.debug("NO WORKFLOW CURRENTLY NEEDS MQ-ACTIVATION")
            continue

        # request activation to MQS
        LOGGER.info(f"REQUESTING ACTIVATION for workflow_id={workflow_id} queues...")
        try:
            mqs_resp = await request_activation_to_mqs(
                wms_db.workflows_collection,
                mqs_rc,
                workflow_id,
            )
        except requests.exceptions.HTTPError as e:
            LOGGER.exception(e)
            continue

        # update the database according to the MQS's response
        if mqs_resp.get("try_again_later"):
            await record_mq_activation_failed(
                wms_db.taskforces_collection,
                workflow_id,
                "MQS responded with 'try_again_later' signal",
            )
            short_sleep = True  # want to give other tasks a chance to start up
            continue
        else:
            await advance_workflows_taskforces_to_prelaunch(
                wms_db.taskforces_collection,
                workflow_id,
            )
