"""REST handlers for grabbing JSON-schema for any route."""


import logging

from . import auth
from .base_handlers import BaseWMSHandler

LOGGER = logging.getLogger(__name__)


class SchemaHandler(BaseWMSHandler):  # pylint: disable=W0223
    """The sole handler for retrieving the OpenAPI schema."""

    ROUTE = r"/schema/openapi$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    async def get(self) -> None:
        """Handle GET."""
        self.write({})