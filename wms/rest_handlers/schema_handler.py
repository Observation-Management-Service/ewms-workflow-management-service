"""REST handlers for grabbing JSON-schema for any route."""


import logging

from .. import config
from . import auth, utils
from .base_handlers import BaseWMSHandler

LOGGER = logging.getLogger(__name__)

openapi_validator = utils.OpenAPIValidator(config.REST_OPENAPI_SPEC, config.ENV.CI_TEST)



class SchemaHandler(BaseWMSHandler):  # pylint: disable=W0223
    """The sole handler for retrieving the OpenAPI schema."""

    ROUTE = r"/schema/openapi$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def get(self) -> None:
        """Handle GET."""
        # get the underlying dict (json)
        openapi_validator.write_and_validate(
            self,
            config.REST_OPENAPI_SPEC.spec.contents(),
        )
