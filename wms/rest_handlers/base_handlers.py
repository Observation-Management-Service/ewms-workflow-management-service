"""Base REST handlers for the WMS REST API server interface."""


import logging
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient
from rest_tools.server import RestHandler

from .. import config
from .. import database as db
from . import auth, utils

LOGGER = logging.getLogger(__name__)

openapi_validator = utils.OpenAPIValidator(config.REST_OPENAPI_SPEC, config.ENV.CI)


class BaseWMSHandler(RestHandler):  # pylint: disable=W0223
    """BaseWMSHandler is a RestHandler for all WMS routes."""

    def initialize(  # type: ignore  # pylint: disable=W0221
        self,
        mongo_client: AsyncIOMotorClient,  # type: ignore[valid-type]
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize a BaseWMSHandler object."""
        super().initialize(*args, **kwargs)  # type: ignore[no-untyped-call]
        # pylint: disable=W0201
        self.task_directives = db.task_directive.TaskDirectiveMongoClient(mongo_client)
        self.backlog = db.backlog.BacklogMongoClient(mongo_client)


# ----------------------------------------------------------------------------


class MainHandler(BaseWMSHandler):  # pylint: disable=W0223
    """MainHandler is a BaseWMSHandler that handles the root route."""

    ROUTE = r"/$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def get(self) -> None:
        """Handle GET."""
        self.write({})


# -----------------------------------------------------------------------------

# ALL OTHER HANDLERS GO IN DEDICATED MODULES
