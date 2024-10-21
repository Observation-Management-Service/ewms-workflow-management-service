"""REST handlers for workflow-related routes."""

import logging
import time

from rest_tools.server import validate_request
from tornado import web

from . import auth, utils
from .base_handlers import BaseWMSHandler
from .task_handlers import create_task_directive_and_taskforces
from .. import config
from ..database.client import DocumentNotFoundException
from ..schema.enums import TaskforcePhase
from ..utils import IDFactory

LOGGER = logging.getLogger(__name__)


def _get_all_queues(tasks: list[dict]) -> list[str]:
    all_queues: list[str] = []
    for td in tasks:
        all_queues.extend(td["input_queue_aliases"])
        all_queues.extend(td["output_queue_aliases"])
    return list(set(all_queues))


# ----------------------------------------------------------------------------


class WorkflowHandler(BaseWMSHandler):  # pylint: disable=W0223
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
            "priority": 10,  # TODO
            # MUTABLE
            "mq_activated_ts": None,  # updated by workflow_mq_activator
            "_mq_activation_retry_at_ts": config.MQS_RETRY_AT_TS_DEFAULT_VALUE,  # updated by workflow_mq_activator,
            "aborted": False,
        }

        # Reserve queues with MQS -- map to aliases
        resp = await self.mqs_rc.request(
            "POST",
            f"/v0/mqs/workflows/{workflow['workflow_id']}/mq-group/reservation",
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
            td, tfs = await create_task_directive_and_taskforces(
                workflow["workflow_id"],  # type: ignore
                #
                task_input["cluster_locations"],
                task_input["task_image"],
                task_input["task_args"],
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
                utils.add_values_to_pilot_config(task_input),
                task_input["worker_config"],
                task_input["n_workers"],
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


# ----------------------------------------------------------------------------


class WorkflowIDHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for a workflow."""

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

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def delete(self, workflow_id: str) -> None:
        """Handle DELETE.

        Abort all tasks in workflow.
        """
        async with await self.wms_db.mongo_client.start_session() as s:
            async with s.start_transaction():  # atomic
                # WORKFLOW
                try:
                    await self.wms_db.workflows_collection.find_one_and_update(
                        {
                            "workflow_id": workflow_id,
                            "aborted": {"$nin": [True]},  # "not in"
                        },
                        {
                            "$set": {"aborted": True},
                        },
                        session=s,
                    )
                except DocumentNotFoundException as e:
                    raise web.HTTPError(
                        status_code=404,
                        reason=f"no non-aborted workflow found with {workflow_id=}",  # to client
                    ) from e

                # TASKFORCES
                # set all corresponding taskforces to pending-stopper
                n_tfs_updated = 0  # in no taskforces to stop (excepted exception)
                try:
                    n_tfs_updated = await self.wms_db.taskforces_collection.update_many(
                        {
                            "workflow_id": workflow_id,
                            # not already aborted
                            # NOTE - we don't care whether the taskforce has started up (see /tms/pending-stopper/taskforces)
                            "phase": {
                                "$nin": [
                                    TaskforcePhase.PENDING_STOPPER,
                                    TaskforcePhase.CONDOR_RM,
                                    TaskforcePhase.CONDOR_COMPLETE,
                                ]
                            },  # "not in"
                        },
                        {
                            "$set": {
                                "phase": TaskforcePhase.PENDING_STOPPER,
                            },
                            "$push": {
                                "phase_change_log": {
                                    "target_phase": TaskforcePhase.PENDING_STOPPER,
                                    "timestamp": time.time(),
                                    "was_successful": True,
                                    "actor": "User",
                                    "description": "User aborted task",
                                },
                            },
                        },
                        session=s,
                    )
                except DocumentNotFoundException:
                    LOGGER.info(
                        "okay scenario: workflow's tasks aborted but no taskforces needed to be stopped"
                    )

        self.write(
            {
                "workflow_id": workflow_id,
                "n_taskforces": n_tfs_updated,
            }
        )


# ----------------------------------------------------------------------------


class WorkflowsFindHandler(BaseWMSHandler):  # pylint: disable=W0223
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


# ----------------------------------------------------------------------------
