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
        """Handle POST.

        Update taskforces' ongoing statuses of its workers.
        """
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

        not_founds = []

        # put in db
        for uuid in all_uuids:
            update = {}
            if uuid in top_task_errors_by_taskforce:
                # value could be falsy -- that's ok
                update["top_task_errors"] = top_task_errors_by_taskforce[uuid]
            if uuid in compound_statuses_by_taskforce:
                # value could be falsy -- that's ok
                update["compound_statuses"] = compound_statuses_by_taskforce[uuid]

            try:
                await self.taskforces_client.update_set_one(
                    {
                        "taskforce_uuid": uuid,
                        "tms_most_recent_action": {"$in": ["condor-submit"]},
                    },
                    update,
                )
            except DocumentNotFoundException:
                LOGGER.warning(f"no running taskforce found with uuid: {uuid}")
                not_founds.append(uuid)

        # respond
        if not_founds:
            self.set_status(207)  # Multi-Status -- not quite a full error
        self.write(
            {
                "results": [  # failures
                    {
                        "uuid": u,
                        "status": "failed",
                        "error": "no running taskforce found with uuid",
                    }
                    for u in not_founds
                ]
                + [  # successes
                    {
                        "uuid": u,
                        "status": "updated",
                    }
                    for u in all_uuids
                    if u not in not_founds
                ]
            }
        )


# ----------------------------------------------------------------------------


class TaskforcesFindHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for finding taskforces."""

    ROUTE = r"/tms/taskforces/find$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    @utils.validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self) -> None:
        """Handle POST.

        Search for taskforces matching given query.
        """
        matches = []
        async for m in self.taskforces_client.find_all(
            self.get_argument("query"),
            self.get_argument("projection", []),
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
        """Handle GET.

        Get the next taskforce to START, for the given condor location.
        """
        try:
            taskforce = await self.taskforces_client.find_one(
                dict(
                    collector=self.get_argument("collector"),
                    schedd=self.get_argument("schedd"),
                    tms_most_recent_action="pending-starter",
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
        """Handle POST.

        Confirm that the taskforce is running and supply condor runtime
        info.
        """
        try:
            await self.taskforces_client.update_set_one(
                {
                    "taskforce_uuid": taskforce_uuid,
                    "tms_most_recent_action": {"$in": ["pending-starter"]},
                },
                dict(
                    cluster_id=self.get_argument("cluster_id"),
                    n_workers=self.get_argument("n_workers"),
                    submit_dict=self.get_argument("submit_dict"),
                    job_event_log_fpath=self.get_argument("job_event_log_fpath"),
                    tms_most_recent_action="condor-submit",
                ),
            )
        except DocumentNotFoundException as e:
            raise web.HTTPError(
                status_code=404,
                reason=f"no 'pending-starter' taskforce found with uuid: {taskforce_uuid}",  # to client
            ) from e

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
        """Handle GET.

        Get the next taskforce to STOP, for the given condor location.
        """
        try:
            taskforce = await self.taskforces_client.find_one(
                {
                    "collector": self.get_argument("collector"),
                    "schedd": self.get_argument("schedd"),
                    "tms_most_recent_action": "pending-stopper",
                    "cluster_id": {"$ne": None},  # there has to be something to stop
                },
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
        """Handle DELETE.

        Confirm that the taskforce has been stopped (condor_rm has been
        invoked).
        """
        try:
            await self.taskforces_client.update_set_one(
                {
                    "taskforce_uuid": taskforce_uuid,
                    # NOTE: any taskforce can be marked as 'condor-rm' regardless of state
                },
                {
                    "tms_most_recent_action": "condor-rm",
                },
            )
        except DocumentNotFoundException as e:
            raise web.HTTPError(
                status_code=404,
                reason=f"no taskforce found with uuid: {taskforce_uuid}",  # to client
            ) from e

        self.write(
            {
                "taskforce_uuid": taskforce_uuid,
            }
        )


# ----------------------------------------------------------------------------


class TaskforceCondorCompleteUUIDHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with a condor-completed taskforce."""

    ROUTE = r"/tms/taskforce/condor-complete/(?P<taskforce_uuid>\w+)$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.TMS])  # type: ignore
    @utils.validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self, taskforce_uuid: str) -> None:
        """Handle POST.

        Supply the timestamp for when the taskforce's condor cluster
        finished, regardless if it ended in success or failure.
        """
        try:
            await self.taskforces_client.update_set_one(
                {
                    "taskforce_uuid": taskforce_uuid,
                    "condor_complete_ts": None,
                },
                {
                    "condor_complete_ts": int(self.get_argument("condor_complete_ts")),
                },
            )
        except DocumentNotFoundException as e:
            raise web.HTTPError(
                status_code=404,
                reason=f"no non-condor-completed taskforce found with uuid: {taskforce_uuid}",  # to client
            ) from e

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
        """Handle GET.

        Get an existing taskforce object.
        """
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
