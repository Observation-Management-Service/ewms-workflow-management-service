"""REST handlers for taskforce-related routes."""


import logging

from .. import config
from . import auth, utils
from .base_handlers import BaseWMSHandler

LOGGER = logging.getLogger(__name__)

openapi_validator = utils.OpenAPIValidator(config.REST_OPENAPI_SPEC)


# ----------------------------------------------------------------------------


class TaskforcesReportHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with reports for taskforce(s)."""

    ROUTE = r"/tms/taskforces/report$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.TMS])  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def post(self) -> None:
        """Handle POST."""
        top_task_errors_by_taskforce = self.get_argument("top_task_errors_by_taskforce")
        compound_statuses_by_taskforce = self.get_argument(
            "compound_statuses_by_taskforce"
        )
        self.write(
            {
                "uuids": list(
                    set(
                        top_task_errors_by_taskforce.keys()
                        + compound_statuses_by_taskforce.keys()
                    )
                )
            }
        )


# ----------------------------------------------------------------------------


class TaskforcesFindHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for finding taskforces."""

    ROUTE = r"/tms/taskforces/find$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def post(self) -> None:
        """Handle POST."""
        self.write(
            {
                "taskforces": [
                    {
                        "taskforce_uuid": "99999cccccc",
                        "foo": 123,
                        "bar": 456,
                        "is_deleted": False,
                    }
                ]
            }
        )


# ----------------------------------------------------------------------------


class TaskforcePendingHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with a pending taskforce."""

    ROUTE = r"/tms/taskforce/pending$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def get(self) -> None:
        """Handle GET."""
        self.write(
            {
                "taskforce_uuid": "99999cccccc",
                "foo": 123,
                "bar": 456,
                "is_deleted": False,
            }
        )


# ----------------------------------------------------------------------------


class TaskforceRunningUUIDHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with a running taskforce."""

    ROUTE = r"/tms/taskforce/running/(?P<taskforce_uuid>\w+)$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.TMS])  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def post(self, taskforce_uuid: str) -> None:
        """Handle POST."""
        self.write(
            {
                "taskforce_uuid": taskforce_uuid,
                "foo": 123,
                "bar": 456,
                "is_deleted": False,
            }
        )


# ----------------------------------------------------------------------------


class TaskforceStopHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with a taskforce designated to be stopped."""

    ROUTE = r"/tms/taskforce/stop$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def get(self) -> None:
        """Handle GET."""
        self.write(
            {
                "taskforce_uuid": "99999cccccc",
                "foo": 123,
                "bar": 456,
                "is_deleted": False,
            }
        )


# ----------------------------------------------------------------------------


class TaskforceStopUUIDHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with a stopped taskforce."""

    ROUTE = r"/tms/taskforce/stop/(?P<taskforce_uuid>\w+)$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.TMS])  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def delete(self, taskforce_uuid: str) -> None:
        """Handle DELETE."""
        self.write(
            {
                "taskforce_uuid": taskforce_uuid,
                "foo": 123,
                "bar": 456,
                "is_deleted": True,
            }
        )


# ----------------------------------------------------------------------------


class TaskforceUUIDHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for a taskforce."""

    ROUTE = r"/tms/taskforce/(?P<taskforce_uuid>\w+)$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def get(self, taskforce_uuid: str) -> None:
        """Handle GET."""
        self.write(
            {
                "taskforce_uuid": taskforce_uuid,
                "foo": 123,
                "bar": 456,
                "is_deleted": False,
            }
        )


# ----------------------------------------------------------------------------
