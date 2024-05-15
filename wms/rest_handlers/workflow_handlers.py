"""REST handlers for workflow-related routes."""

import logging
import time
import uuid

from rest_tools.server import validate_request
from tornado import web

from . import auth
from .base_handlers import BaseWMSHandler
from .task_handlers import create_task_directive
from .. import config
from ..database.client import DocumentNotFoundException
from ..schema.enums import TaskforcePhase

LOGGER = logging.getLogger(__name__)


def _get_all_queues(tasks: list[dict]) -> list[str]:
    all_queues: set[str] = set()
    all_queues.update(td["input_queue_aliases"] for td in tasks)
    all_queues.update(td["output_queue_aliases"] for td in tasks)
    return list(all_queues)


# ----------------------------------------------------------------------------


class WorkflowHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for adding a workflow."""

    ROUTE = r"/workflow$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self) -> None:
        """Handle POST.

        Create a new workflow.
        """

        # make workflow object, put in db
        workflow = dict(
            # IMMUTABLE
            workflow_id=str(uuid.uuid4()),
            timestamp=int(time.time()),
            priority=10,  # TODO
            # MUTABLE
            mq_activated_ts=None,  # updated by task_mq_assembly
            _mqs_retry_at_ts=config.MQS_RETRY_AT_TS_DEFAULT_VALUE,  # updated by task_mq_assembly,
            aborted=False,
        )
        workflow = await self.workflows_client.insert_one(workflow)

        # Reserve queues with MQS -- map to aliases
        resp = await self.mqs_rc.request(
            "POST",
            "/mq-group/reserve",
            {
                "queue_aliases": _get_all_queues(self.get_argument("tasks")),
                "public": self.get_argument("public_queues"),
            },
        )
        mqprofiles = resp["mqprofiles"]

        # Add task directives (and taskforces)
        task_directives = []
        taskforces = []
        for task_input in self.get_argument("tasks"):
            td, tfs = await create_task_directive(
                workflow["workflow_id"],  # type: ignore
                #
                task_input["cluster_locations"],
                task_input["task_image"],
                task_input["task_args"],
                #
                [  # map aliases to ids
                    p["id"]
                    for p in mqprofiles
                    if p["alias"] in resp["input_queue_aliases"]
                ],
                [  # map aliases to ids
                    p["id"]
                    for p in mqprofiles
                    if p["alias"] in resp["output_queue_aliases"]
                ],
                #
                task_input["worker_config"],
                task_input["n_workers"],
                task_input.get("environment", {}),
                task_input.get("input_files", []),
            )
            task_directives.append(td)
            taskforces.extend(tfs)
        task_directives = await self.task_directives_client.insert_many(task_directives)
        taskforces = await self.taskforces_client.insert_many(taskforces)

        # finish up
        self.write(
            dict(
                workflow=workflow,
                task_directives=task_directives,
                taskforces=taskforces,
            )
        )


# ----------------------------------------------------------------------------


class WorkflowIDHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for a workflow."""

    ROUTE = r"/workflow/(?P<workflow_id>\w+)$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def get(self, workflow_id: str) -> None:
        """Handle GET.

        Get an existing workflow.
        """
        try:
            workflow = await self.workflows_client.find_one(
                {
                    "workflow_id": workflow_id,
                }
            )
        except DocumentNotFoundException as e:
            raise web.HTTPError(
                status_code=404,
                reason=f"no task found with id: {workflow_id}",  # to client
            ) from e

        self.write(workflow)

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def delete(self, workflow_id: str) -> None:
        """Handle DELETE.

        Abort all tasks in workflow.
        """

        # WORKFLOW
        try:
            await self.workflows_client.find_one_and_update(
                {
                    "workflow_id": workflow_id,
                    "aborted": {"$nin": [True]},  # "not in"
                },
                {
                    "aborted": True,
                },
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
            n_tfs_updated = await self.taskforces_client.update_set_many(
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
