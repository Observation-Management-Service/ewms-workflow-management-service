"""REST handlers for workflow-related routes."""

import logging
import time
import uuid

from rest_tools.server import validate_request
from tornado import web

from . import auth
from .base_handlers import BaseWMSHandler
from .task_handlers import create_task_directive_and_taskforces
from .. import config
from ..database.client import DocumentNotFoundException
from ..schema.enums import TaskforcePhase

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

    ROUTE = r"/workflows$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self) -> None:
        """Handle POST.

        Create a new workflow.
        """
        workflow = {
            # IMMUTABLE
            "workflow_id": uuid.uuid4().hex,
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
            "/v0/mq-group/reservation",
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
                task_input["worker_config"],
                task_input["n_workers"],
                task_input.get("environment", {}),
                task_input.get("input_files", []),
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

    ROUTE = r"/workflows/(?P<workflow_id>\w+)$"

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
                            "aborted": True,
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
                    n_tfs_updated = await self.wms_db.taskforces_collection.update_set_many(
                        {
                            "workflow_id": workflow_id,
                            "$and": [
                                # not already aborted
                                # NOTE - we don't care whether the taskforce has started up (see /taskforce/tms-action/pending-stopper)
                                {
                                    "phase": {
                                        "$nin": [
                                            TaskforcePhase.PENDING_STOPPER,
                                            TaskforcePhase.CONDOR_RM,
                                        ]
                                    },  # "not in"
                                },
                                # AND
                                # not condor-completed
                                {
                                    "condor_complete_ts": None,  # int -> condor-completed
                                },
                            ],
                        },
                        {
                            "phase": TaskforcePhase.PENDING_STOPPER,
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

    ROUTE = r"/workflows/find$"

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
