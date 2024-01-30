"""Base REST handlers for the WMS REST API server interface."""


import logging
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient
from rest_tools.server import RestHandler

from .. import database
from . import auth

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
        self.task_directives = database.interface.TaskDirectivesClient(mongo_client)
        self.backlog = database.interface.BacklogClient(mongo_client)


# ----------------------------------------------------------------------------


class MainHandler(BaseWMSHandler):  # pylint: disable=W0223
    """MainHandler is a BaseWMSHandler that handles the root route."""

    ROUTE = r"/$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    async def get(self) -> None:
        """Handle GET."""
        self.write({})


# -----------------------------------------------------------------------------

# ALL OTHER HANDLERS GO IN DEDICATED MODULES
