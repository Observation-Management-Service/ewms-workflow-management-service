"""REST handlers for taskforce-related routes."""

import logging

from pymongo import ASCENDING, DESCENDING
from rest_tools.server import validate_request
from tornado import web

from . import auth
from .base_handlers import BaseWMSHandler
from .. import config
from ..database.client import DocumentNotFoundException
from ..schema.enums import TaskforcePhase

LOGGER = logging.getLogger(__name__)


# ----------------------------------------------------------------------------


class TaskforcesReportHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with statuses for taskforce(s)."""

    ROUTE = r"/taskforces/tms/status$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.TMS])  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self) -> None:
        """Handle POST.

        Update taskforces' statuses of its workers.
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
                await self.taskforces_client.find_one_and_update(
                    {
                        "taskforce_uuid": uuid,
                        # we don't care what the 'phase' is
                    },
                    update,
                )
            except DocumentNotFoundException:
                LOGGER.warning(f"no taskforce found with uuid: {uuid}")
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
                        "error": "no taskforce found with uuid",
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

    ROUTE = r"/taskforces/find$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
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


class TaskforcePendingStarterHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with a pending taskforce."""

    ROUTE = r"/taskforce/tms-action/pending-starter$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def get(self) -> None:
        """Handle GET.

        Get the next taskforce to START for the given condor location.
        """
        try:
            taskforce = await self.taskforces_client.find_one(
                dict(
                    collector=self.get_argument("collector"),
                    schedd=self.get_argument("schedd"),
                    phase=TaskforcePhase.PENDING_STARTER,
                ),
                sort=[
                    ("worker_config.priority", DESCENDING),  # first, highest priority
                    ("timestamp", ASCENDING),  # then, oldest
                ],
            )
        except DocumentNotFoundException:
            taskforce = {}

        self.write(taskforce)


# ----------------------------------------------------------------------------


class TaskforceCondorSubmitUUIDHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with a condor-submitted taskforce."""

    ROUTE = r"/taskforce/tms-action/condor-submit/(?P<taskforce_uuid>\w+)$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.TMS])  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self, taskforce_uuid: str) -> None:
        """Handle POST.

        Confirm that the taskforce is condor-submitted and supply condor
        runtime info.
        """
        try:
            await self.taskforces_client.find_one_and_update(
                {
                    "taskforce_uuid": taskforce_uuid,
                    "phase": {"$in": [TaskforcePhase.PENDING_STARTER]},
                },
                dict(
                    cluster_id=self.get_argument("cluster_id"),
                    n_workers=self.get_argument("n_workers"),
                    submit_dict=self.get_argument("submit_dict"),
                    job_event_log_fpath=self.get_argument("job_event_log_fpath"),
                    phase=TaskforcePhase.CONDOR_SUBMIT,
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


class TaskforcePendingStopperHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for the top taskforce designated to be stopped."""

    ROUTE = r"/taskforce/tms-action/pending-stopper$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def get(self) -> None:
        """Handle GET.

        Get the next taskforce to STOP for the given condor location.
        """
        try:
            taskforce = await self.taskforces_client.find_one(
                {
                    "collector": self.get_argument("collector"),
                    "schedd": self.get_argument("schedd"),
                    "phase": TaskforcePhase.PENDING_STOPPER,
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


class TaskforcePendingStopperUUIDHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with a taskforce designated to be stopped."""

    ROUTE = r"/taskforce/tms-action/pending-stopper/(?P<taskforce_uuid>\w+)$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.TMS])  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def delete(self, taskforce_uuid: str) -> None:
        """Handle DELETE.

        Confirm that the taskforce has been stopped (condor_rm has been
        invoked).
        """
        try:
            await self.taskforces_client.find_one_and_update(
                {
                    "taskforce_uuid": taskforce_uuid,
                    # NOTE: any taskforce can be marked as 'condor-rm' regardless of state
                },
                {
                    "phase": TaskforcePhase.CONDOR_RM,
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

    ROUTE = r"/taskforce/tms/condor-complete/(?P<taskforce_uuid>\w+)$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.TMS])  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self, taskforce_uuid: str) -> None:
        """Handle POST.

        Supply the timestamp for when the taskforce's condor cluster
        finished, regardless if it ended in success or failure.
        """
        try:
            await self.taskforces_client.find_one_and_update(
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

    ROUTE = r"/taskforce/(?P<taskforce_uuid>\w+)$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
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
