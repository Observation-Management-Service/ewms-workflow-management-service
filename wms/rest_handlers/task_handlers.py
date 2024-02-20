"""REST handlers for task-related routes."""


import logging
import time
import uuid

from tornado import web

from .. import config
from ..database.client import DocumentNotFoundException
from . import auth, utils
from .base_handlers import BaseWMSHandler

LOGGER = logging.getLogger(__name__)


# ----------------------------------------------------------------------------


class TaskDirectiveHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for adding a task directive (initiating a task)."""

    ROUTE = r"/task/directive$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @utils.validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self) -> None:
        """Handle POST."""
        task_directive = dict(
            task_id=uuid.uuid4().hex,
            cluster_locations=self.get_argument("cluster_locations"),
            task_image=self.get_argument("task_image"),
            task_args=self.get_argument("task_args", ""),
            timestamp=int(time.time()),
            terminated=False,
        )

        # first, check that locations are legit
        for location in task_directive["cluster_locations"]:
            if location not in config.KNOWN_CLUSTERS:
                raise web.HTTPError(
                    status_code=400,
                    reason=f"condor location not found: {location}",  # to client
                )

        # next, insert
        task_directive = await self.task_directives_client.insert_one(task_directive)

        # now, create Taskforce entries (important to do now so removals are handled easily--think dangling pointers)
        # TODO - set tms_status to 'backlog', then backlogger changes to 'pending-start'
        for location in task_directive["cluster_locations"]:
            await self.taskforces_client.insert_one(
                dict(
                    taskforce_uuid=uuid.uuid4().hex,
                    task_id=task_directive["task_id"],
                    timestamp=int(time.time()),
                    collector=config.KNOWN_CLUSTERS[location]["collector"],
                    schedd=config.KNOWN_CLUSTERS[location]["schedd"],
                    #
                    # set by tms via /tms/taskforce/running/<id>
                    cluster_id=None,
                    n_workers=None,
                    submit_dict={},
                    job_event_log_fpath="",
                    #
                    # updated by tms several times
                    tms_status="pending-start",
                    compound_statuses={},
                    top_task_errors={},
                )
            )

        self.write(task_directive)


# ----------------------------------------------------------------------------


class TaskDirectiveIDHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for a task's directive."""

    ROUTE = r"/task/directive/(?P<task_id>\w+)$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @utils.validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def get(self, task_id: str) -> None:
        """Handle GET."""
        try:
            task_directive = await self.task_directives_client.find_one(
                {
                    "task_id": task_id,
                }
            )
        except DocumentNotFoundException as e:
            raise web.HTTPError(
                status_code=404,
                reason=f"no task found with id: {task_id}",  # to client
            ) from e

        self.write(task_directive)

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @utils.validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def delete(self, task_id: str) -> None:
        """Handle DELETE."""

        # NOTE: it may be useful to add a 'reason' enum to distinguish normal vs forced terminations

        try:
            await self.task_directives_client.update_set_one(
                {
                    "task_id": task_id,
                },
                {
                    "terminated": True,
                },
            )
        except DocumentNotFoundException as e:
            raise web.HTTPError(
                status_code=404,
                reason=f"no task found with id: {task_id}",  # to client
            ) from e

        # set all corresponding taskforces to pending-stop
        n_updated = await self.taskforces_client.update_set_many(
            {
                "task_id": task_id,
            },
            {
                "tms_status": "pending-stop",
            },
        )

        self.write({"task_id": task_id, "n_taskforces": n_updated})


# ----------------------------------------------------------------------------


class TaskDirectivesFindHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for finding task directives."""

    ROUTE = r"/task/directives/find$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @utils.validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self) -> None:
        """Handle POST."""
        matches = []
        async for m in self.task_directives_client.find_all(
            self.get_argument("query"),
            self.get_argument("projection", []),
        ):
            matches.append(m)

        self.write({"task_directives": matches})


# ----------------------------------------------------------------------------
