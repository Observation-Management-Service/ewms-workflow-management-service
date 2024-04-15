"""Base REST handlers for the WMS REST API server interface."""

import logging
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient
from rest_tools.server import RestHandler
from rest_tools.server import validate_request

from . import auth
from .. import config
from .. import database as db

LOGGER = logging.getLogger(__name__)


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
        self.task_directives_client = db.client.WMSMongoClient(
            mongo_client,
            db.utils.TASK_DIRECTIVES_COLL_NAME,
        )
        self.taskforces_client = db.client.WMSMongoClient(
            mongo_client,
            db.utils.TASKFORCES_COLL_NAME,
        )


# ----------------------------------------------------------------------------


class MainHandler(BaseWMSHandler):  # pylint: disable=W0223
    """MainHandler is a BaseWMSHandler that handles the root route."""

    ROUTE = r"/$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def get(self) -> None:
        """Handle GET."""
        self.write({})


# -----------------------------------------------------------------------------

# ALL OTHER HANDLERS GO IN DEDICATED MODULES
