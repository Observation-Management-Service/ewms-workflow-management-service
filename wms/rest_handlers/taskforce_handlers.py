"""REST handlers for taskforce-related routes."""


import logging

from pymongo import ASCENDING
from tornado import web

from .. import config
from ..database.client import DocumentNotFoundException
from . import auth, utils
from .base_handlers import BaseWMSHandler

LOGGER = logging.getLogger(__name__)


# ----------------------------------------------------------------------------


class TaskforcesReportHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with reports for taskforce(s)."""

    ROUTE = r"/tms/taskforces/report$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.TMS])  # type: ignore
    @utils.validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self) -> None:
        """Handle POST."""
        top_task_errors_by_taskforce = self.get_argument(
            "top_task_errors_by_taskforce", default={}
        )
        compound_statuses_by_taskforce = self.get_argument(
            "compound_statuses_by_taskforce", default={}
        )

        all_uuids = list(
            set(
                list(top_task_errors_by_taskforce.keys())
                + list(compound_statuses_by_taskforce.keys())
            )
        )

        # put in db
        for uuid in all_uuids:
            update = {}
            if uuid in top_task_errors_by_taskforce:
                # value could be falsy -- that's ok
                update["top_task_errors"] = top_task_errors_by_taskforce[uuid]
            if uuid in compound_statuses_by_taskforce:
                # value could be falsy -- that's ok
                update["compound_statuses"] = compound_statuses_by_taskforce[uuid]

            await self.taskforces_client.update_set_one(
                {"taskforce_uuid": uuid},
                update,
            )

        self.write({"uuids": all_uuids})


# ----------------------------------------------------------------------------


class TaskforcesFindHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for finding taskforces."""

    ROUTE = r"/tms/taskforces/find$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    @utils.validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self) -> None:
        """Handle POST."""
        matches = []
        async for m in self.taskforces_client.find_all(
            self.get_argument("query"),
            self.get_argument("projection", {}),
        ):
            matches.append(m)

        self.write({"taskforces": matches})


# ----------------------------------------------------------------------------


class TaskforcePendingHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with a pending taskforce."""

    ROUTE = r"/tms/taskforce/pending$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    @utils.validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def get(self) -> None:
        """Handle GET."""

        # get the next taskforce to START, for the given cluster
        try:
            taskforce = await self.taskforces_client.find_one(
                dict(
                    collector=self.get_argument("collector"),
                    schedd=self.get_argument("schedd"),
                    tms_status="pending-start",
                ),
                sort=[
                    ("timestamp", ASCENDING),  # oldest first
                ],
            )
        except DocumentNotFoundException:
            taskforce = {}

        self.write(taskforce)


# ----------------------------------------------------------------------------


class TaskforceRunningUUIDHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with a running taskforce."""

    ROUTE = r"/tms/taskforce/running/(?P<taskforce_uuid>\w+)$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.TMS])  # type: ignore
    @utils.validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self, taskforce_uuid: str) -> None:
        """Handle POST."""
        await self.taskforces_client.update_set_one(
            {
                "taskforce_uuid": taskforce_uuid,
            },
            dict(
                cluster_id=self.get_argument("cluster_id"),
                n_workers=self.get_argument("n_workers"),
                submit_dict=self.get_argument("submit_dict"),
                job_event_log_fpath=self.get_argument("job_event_log_fpath"),
                tms_status="running",
            ),
        )

        self.write(
            {
                "taskforce_uuid": taskforce_uuid,
            }
        )


# ----------------------------------------------------------------------------


class TaskforceStopHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with a taskforce designated to be stopped."""

    ROUTE = r"/tms/taskforce/stop$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    @utils.validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def get(self) -> None:
        """Handle GET."""

        # get the next taskforce to STOP, for the given cluster
        try:
            taskforce = await self.taskforces_client.find_one(
                dict(
                    collector=self.get_argument("collector"),
                    schedd=self.get_argument("schedd"),
                    tms_status="pending-stop",
                ),
                sort=[
                    ("timestamp", ASCENDING),  # oldest first
                ],
            )
        except DocumentNotFoundException:
            taskforce = {}

        self.write(taskforce)


# ----------------------------------------------------------------------------


class TaskforceStopUUIDHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with a stopped taskforce."""

    ROUTE = r"/tms/taskforce/stop/(?P<taskforce_uuid>\w+)$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.TMS])  # type: ignore
    @utils.validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def delete(self, taskforce_uuid: str) -> None:
        """Handle DELETE."""

        await self.taskforces_client.update_set_one(
            {
                "taskforce_uuid": taskforce_uuid,
            },
            {
                "tms_status": "done",
            },
        )

        self.write(
            {
                "taskforce_uuid": taskforce_uuid,
            }
        )


# ----------------------------------------------------------------------------


class TaskforceUUIDHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for a taskforce."""

    ROUTE = r"/tms/taskforce/(?P<taskforce_uuid>\w+)$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    @utils.validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def get(self, taskforce_uuid: str) -> None:
        """Handle GET."""

        try:
            taskforce = await self.taskforces_client.find_one(
                {
                    "taskforce_uuid": taskforce_uuid,
                }
            )
        except DocumentNotFoundException as e:
            raise web.HTTPError(
                status_code=404,
                reason=f"no taskforce found with uuid: {taskforce_uuid}",  # to client
            ) from e

        self.write(taskforce)


# ----------------------------------------------------------------------------
