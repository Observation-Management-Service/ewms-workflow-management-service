"""REST handlers for task-related routes."""


import logging

from .. import config
from . import auth, utils
from .base_handlers import BaseWMSHandler

LOGGER = logging.getLogger(__name__)

openapi_validator = utils.OpenAPIValidator(config.REST_OPENAPI_SPEC)


class TaskDirectiveHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for adding a task directive (initiating a task)."""

    ROUTE = r"/task/directive$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def post(self) -> None:
        """Handle POST."""
        self.write({"foo": 1, "bar": 2, "task_id": "abcdef123456"})


# ----------------------------------------------------------------------------


class TaskDirectiveIDHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for a task's directive."""

    ROUTE = r"/task/directive/(?P<task_id>\w+)$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def get(self, task_id: str) -> None:
        """Handle GET."""
        self.write({"foo": 1, "bar": 2, "task_id": "abcdef123456"})


# ----------------------------------------------------------------------------


class TaskDirectivesFindHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for finding task directives."""

    ROUTE = r"/task/directives/find$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def post(self) -> None:
        """Handle POST."""
        self.write(
            {
                "task_directives": [
                    {"foo": 1, "bar": 2, "task_id": "abcdef123456"},
                ]
            }
        )


# ----------------------------------------------------------------------------
