"""Base REST handlers for the WMS REST API server interface."""

import logging
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient
from rest_tools.server import RestHandler, validate_request

from . import auth
from .. import config, database
from ..utils import get_mqs_connection

LOGGER = logging.getLogger(__name__)


class BaseWMSHandler(RestHandler):
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


# --------------------------------------------------------------------------------------


class MainHandler(BaseWMSHandler):
    """MainHandler is a BaseWMSHandler that handles the root route."""

    ROUTE = rf"/{config.URL_V_PREFIX}/$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def get(self) -> None:
        """Handle GET."""
        self.write({})


# --------------------------------------------------------------------------------------

# ALL OTHER HANDLERS GO IN DEDICATED MODULES
