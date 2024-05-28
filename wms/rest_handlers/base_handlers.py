"""Base REST handlers for the WMS REST API server interface."""

import logging
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient
from rest_tools.server import RestHandler
from rest_tools.server import validate_request

from . import auth
from .. import config
from .. import database
from ..utils import get_mqs_connection

LOGGER = logging.getLogger(__name__)


class BaseWMSHandler(RestHandler):  # pylint: disable=W0223
    """BaseWMSHandler is a RestHandler for all WMS routes."""

    def initialize(  # type: ignore  # pylint: disable=W0221
        self,
        mongo_client: AsyncIOMotorClient,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize a BaseWMSHandler object."""
        super().initialize(*args, **kwargs)  # type: ignore[no-untyped-call]
        self.wms_db = database.client.WMSMongoValidatedDatabase(mongo_client)
        self.mqs_rc = get_mqs_connection(
            logging.getLogger(f"{LOGGER.name.split('.', maxsplit=1)[0]}.mqs")
        )


# ----------------------------------------------------------------------------


class MainHandler(BaseWMSHandler):  # pylint: disable=W0223
    """MainHandler is a BaseWMSHandler that handles the root route."""

    ROUTE = rf"/{config.ROUTE_VERSION_PREFIX}/$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def get(self) -> None:
        """Handle GET."""
        self.write({})


# -----------------------------------------------------------------------------

# ALL OTHER HANDLERS GO IN DEDICATED MODULES
