"""REST handlers for taskforce-related routes."""


import logging

from .. import config
from . import auth, utils
from .base_handlers import BaseWMSHandler

LOGGER = logging.getLogger(__name__)

openapi_validator = utils.OpenAPIValidator(config.REST_OPENAPI_SPEC, config.ENV.CI)


# ----------------------------------------------------------------------------


class TaskforceHandlerUUID(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for a taskforce."""

    ROUTE = r"/tms/taskforce/(?P<taskforce_uuid>\w+)$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def get(self) -> None:
        """Handle GET."""
        openapi_validator.write_and_validate(
            self,
            {},
        )


# ----------------------------------------------------------------------------


class TaskforcesFindHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for finding taskforces."""

    ROUTE = r"/tms/taskforces/find$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def post(self) -> None:
        """Handle POST."""
        openapi_validator.write_and_validate(
            self,
            {},
        )


# ----------------------------------------------------------------------------


class TaskforcePendingHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with a pending taskforce."""

    ROUTE = r"/tms/taskforce/pending$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def get(self) -> None:
        """Handle GET."""
        openapi_validator.write_and_validate(
            self,
            {},
        )


# ----------------------------------------------------------------------------


class TaskforceRunningUUIDHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with a running taskforce."""

    ROUTE = r"/tms/taskforce/running/(?P<taskforce_uuid>\w+)$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.TMS])  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def post(self, taskforce_uuid: str) -> None:
        """Handle POST."""
        openapi_validator.write_and_validate(
            self,
            {},
        )


# ----------------------------------------------------------------------------


class TaskforceStopHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with a taskforce designated to be stopped."""

    ROUTE = r"/tms/taskforce/stop$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def get(self) -> None:
        """Handle GET."""
        openapi_validator.write_and_validate(
            self,
            {},
        )


# ----------------------------------------------------------------------------


class TaskforceStopUUIDHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with a stopped taskforce."""

    ROUTE = r"/tms/taskforce/stop/(?P<taskforce_uuid>\w+)$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.TMS])  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def delete(self, taskforce_uuid: str) -> None:
        """Handle DELETE."""
        openapi_validator.write_and_validate(
            self,
            {},
        )


# ----------------------------------------------------------------------------


class TaskforcesReportHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with reports for taskforce(s)."""

    ROUTE = r"/tms/taskforces/report$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.TMS])  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def post(self) -> None:
        """Handle POST."""
        openapi_validator.write_and_validate(
            self,
            {},
        )


# ----------------------------------------------------------------------------
