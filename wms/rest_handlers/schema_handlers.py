"""REST handlers for grabbing JSON-schema for any route."""


import logging
from typing import Any

from ..schema import rest_schema
from . import auth
from .base_handlers import BaseWMSHandler

LOGGER = logging.getLogger(__name__)


def get_json_schema_handler(objective_route: str) -> type[BaseWMSHandler]:
    """Create a route handler for getting the JSON-schema for route."""
    if not objective_route.startswith("/"):
        raise ValueError(f"objective_route must start with '/': {objective_route}")

    try:
        this_schema = rest_schema.RestSchema[objective_route]
    except KeyError:
        LOGGER.warning(f"this route does not have a JSON-schema: {objective_route}")
        raise

    class JSONSchemaHandler(BaseWMSHandler):  # pylint: disable=W0223
        ROUTE = f"/schema{objective_route}"

        @auth.service_account_auth(roles=[auth.AuthAccounts.USER, auth.AuthAccounts.TMS])  # type: ignore
        async def get(self, *args: Any, **kwargs: Any) -> None:
            self.write(this_schema)

    return JSONSchemaHandler


# ----------------------------------------------------------------------------
