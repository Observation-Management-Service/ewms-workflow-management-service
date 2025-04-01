"""REST handlers for workflow-related routes."""

import logging
import time

from rest_tools.server import validate_request
from tornado import web

from wms import database
from . import auth
from .base_handlers import BaseWMSHandler
from .task_directive_handlers import make_task_directive_object_and_taskforce_objects
from .. import config
from ..config import DEFAULT_WORKFLOW_PRIORITY, MAX_WORKFLOW_PRIORITY, MQS_ROUTE_PREFIX
from ..database.client import DocumentNotFoundException
from ..schema.enums import (
    ENDING_OR_FINISHED_TASKFORCE_PHASES,
    TaskforcePhase,
    WorkflowDeactivatedType,
)
from ..utils import IDFactory

LOGGER = logging.getLogger(__name__)


def _get_all_queues(tasks: list[dict]) -> list[str]:
    all_queues: list[str] = []
    for td in tasks:
        all_queues.extend(td["input_queue_aliases"])
        all_queues.extend(td["output_queue_aliases"])
    return list(set(all_queues))


# --------------------------------------------------------------------------------------


class WorkflowHandler(BaseWMSHandler):
    """Handle actions for adding a workflow."""

    ROUTE = rf"/{config.ROUTE_VERSION_PREFIX}/workflows$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self) -> None:
        """Handle POST.

        Create a new workflow.
        """

        # Advanced validation -- not possible in json schema (FUTURE: if it is, then move to .json)
        for i, task_input in enumerate(self.get_argument("tasks")):
            for bad_env in [
                # pilot-task config
                "EWMS_PILOT_TASK_IMAGE",
                "EWMS_PILOT_TASK_ARGS",
                "EWMS_PILOT_TASK_ENV_JSON",
                # pilot-init config
                "EWMS_PILOT_INIT_IMAGE",
                "EWMS_PILOT_INIT_ARGS",
                "EWMS_PILOT_INIT_ENV_JSON",
            ]:
                if bad_env in task_input.get("pilot_config", {}).get("environment", {}):
                    msg = (
                        f"tasks[{i}].pilot_config.environment cannot include the attribute "
                        f"'{bad_env}'. Use the top-level equivalent attribute instead."
                    )
                    raise web.HTTPError(
                        status_code=400,
                        log_message=msg,  # to stderr
                        reason=msg,  # to client
                    )

        # Assemble
        workflow = {
            # IMMUTABLE
            "workflow_id": IDFactory.generate_workflow_id(),
            "timestamp": time.time(),
            "priority": max(
                self.get_argument("priority", DEFAULT_WORKFLOW_PRIORITY),
                MAX_WORKFLOW_PRIORITY,
            ),
            # MUTABLE
            "deactivated": None,
            "deactivated_ts": None,
        }

        # Reserve queues with MQS -- map to aliases
        resp = await self.mqs_rc.request(
            "POST",
            f"/{MQS_ROUTE_PREFIX}/mqs/workflows/{workflow['workflow_id']}/mq-group/reservation",
            {
                "queue_aliases": _get_all_queues(self.get_argument("tasks")),
                "public": self.get_argument("public_queue_aliases"),
            },
        )
        mqprofiles = resp["mqprofiles"]

        # Add task directives (and taskforces)
        task_directives = []
        taskforces = []
        for task_input in self.get_argument("tasks"):
            td, tfs = await make_task_directive_object_and_taskforce_objects(
                workflow["workflow_id"],  # type: ignore
                workflow["priority"],
                #
                task_input["cluster_locations"],
                #
                task_input["task_image"],
                task_input["task_args"],
                task_input.get("task_env"),  # optional
                #
                task_input.get("init_image"),  # optional
                task_input.get("init_args"),  # optional
                task_input.get("init_env"),  # optional
                #
                #
                [  # map aliases to ids
                    p["mqid"]
                    for p in mqprofiles
                    if p["alias"] in task_input["input_queue_aliases"]
                ],
                [  # map aliases to ids
                    p["mqid"]
                    for p in mqprofiles
                    if p["alias"] in task_input["output_queue_aliases"]
                ],
                #
                {  # add values (default and/or detected)
                    "tag": config.get_pilot_tag(
                        task_input.get("pilot_config", {}).get("tag", "latest")
                    ),
                    "environment": task_input.get("pilot_config", {}).get(
                        "environment", {}
                    ),
                    "input_files": task_input.get("pilot_config", {}).get(
                        "input_files", []
                    ),
                },
                task_input["worker_config"],
                task_input["n_workers"],  # TODO: make optional/smart
            )
            task_directives.append(td)
            taskforces.extend(tfs)

        # put all into db -- atomically
        async with await self.wms_db.mongo_client.start_session() as s:
            async with s.start_transaction():  # atomic
                workflow = await self.wms_db.workflows_collection.insert_one(
                    workflow,
                    session=s,
                )
                task_directives = (
                    await self.wms_db.task_directives_collection.insert_many(
                        task_directives,
                        session=s,
                    )
                )
                taskforces = await self.wms_db.taskforces_collection.insert_many(
                    taskforces,
                    session=s,
                )

        # Finish up
        self.write(
            {
                "workflow": workflow,
                "task_directives": task_directives,
                "taskforces": taskforces,
            }
        )


# --------------------------------------------------------------------------------------


class WorkflowIDHandler(BaseWMSHandler):
    """Handle basic actions on a workflow."""

    ROUTE = rf"/{config.ROUTE_VERSION_PREFIX}/workflows/(?P<workflow_id>[\w-]+)$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def get(self, workflow_id: str) -> None:
        """Handle GET.

        Get an existing workflow.
        """
        try:
            workflow = await self.wms_db.workflows_collection.find_one(
                {
                    "workflow_id": workflow_id,
                }
            )
        except DocumentNotFoundException as e:
            raise web.HTTPError(
                status_code=404,
                reason=f"no workflow found with id: {workflow_id}",  # to client
            ) from e

        self.write(workflow)


# --------------------------------------------------------------------------------------


async def deactivate_workflow(
    wms_db: database.client.WMSMongoValidatedDatabase,
    workflow_id: str,
    deactivated_type: WorkflowDeactivatedType,
):
    """Stop the workflow and mark the taskforces for 'pending-stopper'."""
    async with await wms_db.mongo_client.start_session() as s:
        async with s.start_transaction():  # atomic
            # WORKFLOW
            try:
                await wms_db.workflows_collection.find_one_and_update(
                    {
                        "workflow_id": workflow_id,
                        "deactivated": None,  # aka not deactivated
                    },
                    {
                        "$set": {
                            "deactivated": deactivated_type,
                            "deactivated_ts": time.time(),
                        },
                    },
                    session=s,
                )
            except DocumentNotFoundException as e:
                raise web.HTTPError(
                    status_code=404,
                    reason=f"no non-deactivated workflow found with {workflow_id=}",  # to client
                ) from e

            # TASKFORCES
            # -> push "failed phase change" for any taskforces that *ARE* already ending/finished
            # NOTE: this db call has to happen before the "set to pending-stopper" b/c
            #   otherwise, each taskforce would get "set to pending-stopper" then "failed phase change"
            try:
                await wms_db.taskforces_collection.update_many(
                    {
                        "workflow_id": workflow_id,
                        "phase": {"$in": ENDING_OR_FINISHED_TASKFORCE_PHASES},
                    },
                    {
                        # no "$set" needed, the phase is not changing
                        "$push": {
                            "phase_change_log": {
                                "target_phase": TaskforcePhase.PENDING_STOPPER,
                                "timestamp": time.time(),
                                "source_event_time": None,
                                "was_successful": False,
                                "source_entity": "User",
                                "context": (
                                    f"User deactivated ({deactivated_type}) "
                                    f"workflow but taskforce "
                                    f"is already ending/finished "
                                    f"({", ".join(ENDING_OR_FINISHED_TASKFORCE_PHASES)})"
                                ),
                            },
                        },
                    },
                    session=s,
                )
            except DocumentNotFoundException:
                pass  # it's actually a good thing if there were no matches
            #
            # -> now, set all not-already-ending/finished taskforces to pending-stopper
            n_tfs_updated = 0  # in no taskforces to stop (excepted exception)
            try:
                n_tfs_updated = await wms_db.taskforces_collection.update_many(
                    {
                        "workflow_id": workflow_id,
                        # NOTE: we don't care whether the taskforce's condor cluster
                        #   has started up (see /tms/pending-stopper/taskforces)
                        "phase": {"$nin": ENDING_OR_FINISHED_TASKFORCE_PHASES},
                    },
                    {
                        "$set": {
                            "phase": TaskforcePhase.PENDING_STOPPER,
                        },
                        "$push": {
                            "phase_change_log": {
                                "target_phase": TaskforcePhase.PENDING_STOPPER,
                                "timestamp": time.time(),
                                "source_event_time": None,
                                "was_successful": True,
                                "source_entity": "User",
                                "context": f"User deactivated ({deactivated_type}) workflow",
                            },
                        },
                    },
                    session=s,
                )
            except DocumentNotFoundException:
                LOGGER.info(
                    "okay scenario: workflow deactivated but no taskforces needed to be stopped"
                )

    # all done
    return {
        "workflow_id": workflow_id,
        "n_taskforces": n_tfs_updated,
    }


class WorkflowIDActionsAbortHandler(BaseWMSHandler):
    """Handle aborting a workflow."""

    ROUTE = rf"/{config.ROUTE_VERSION_PREFIX}/workflows/(?P<workflow_id>[\w-]+)/actions/abort$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self, workflow_id: str) -> None:
        """Handle POST.

        Deactivate workflow (type: abort) and stop taskforces.
        """
        out = await deactivate_workflow(
            self.wms_db,
            workflow_id,
            WorkflowDeactivatedType.ABORTED,
        )
        self.write(out)


class WorkflowIDActionsFinishedHandler(BaseWMSHandler):
    """Handle marking a workflow as finished."""

    ROUTE = rf"/{config.ROUTE_VERSION_PREFIX}/workflows/(?P<workflow_id>[\w-]+)/actions/finished$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self, workflow_id: str) -> None:
        """Handle POST.

        Deactivate workflow (type: mark as 'finished') and stop taskforces.
        """
        out = await deactivate_workflow(
            self.wms_db,
            workflow_id,
            WorkflowDeactivatedType.FINISHED,
        )
        self.write(out)


# --------------------------------------------------------------------------------------


class WorkflowsFindHandler(BaseWMSHandler):
    """Handle actions for finding workflows."""

    ROUTE = rf"/{config.ROUTE_VERSION_PREFIX}/query/workflows$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self) -> None:
        """Handle POST.

        Search for workflows matching given query.
        """
        matches = []
        async for m in self.wms_db.workflows_collection.find_all(
            self.get_argument("query"),
            self.get_argument("projection", []),
        ):
            matches.append(m)

        self.write({"workflows": matches})


# --------------------------------------------------------------------------------------
