"""REST handlers for grabbing JSON-schema for any route."""


import logging

from .. import config
from . import auth, utils
from .base_handlers import BaseWMSHandler

LOGGER = logging.getLogger(__name__)

openapi_validator = utils.OpenAPIValidator(config.REST_OPENAPI_SPEC)


class SchemaHandler(BaseWMSHandler):  # pylint: disable=W0223
    """The sole handler for retrieving the OpenAPI schema."""

    ROUTE = r"/schema/openapi$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def get(self) -> None:
        """Handle GET."""
        # get the underlying dict (json)
        self.write(  # NOTE - if this doesn't work then use accessor.open ctx-mgr
            config.REST_OPENAPI_SPEC.accessor.lookup,  # type: ignore[attr-defined]
        )