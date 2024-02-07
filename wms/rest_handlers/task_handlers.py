"""REST handlers for task-related routes."""


import logging

from .. import config
from . import auth, utils
from .base_handlers import BaseWMSHandler

LOGGER = logging.getLogger(__name__)

openapi_validator = utils.OpenAPIValidator(config.REST_OPENAPI_SPEC)


class TaskHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for initiating a task."""

    ROUTE = r"/task$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def post(self) -> None:
        """Handle POST."""
        self.write({})


# ----------------------------------------------------------------------------
