"""utils.py."""

"""Utils for REST routes."""


import logging

from openapi_core import Spec, validate_request, validate_response
from tornado.web import RequestHandler

LOGGER = logging.getLogger(__name__)


class OpenAPIValidator:
    """A helper class for validating requests and responses with openapi."""

    def __init__(self, spec: Spec, testing: bool) -> None:
        self.spec = spec
        self.testing = testing

    def validate_request(self):  # type: ignore
        """Validate request obj against the given OpenAPI spec."""

        def make_wrapper(method):  # type: ignore[no-untyped-def]
            async def wrapper(reqhand: RequestHandler, *args, **kwargs):  # type: ignore[no-untyped-def]
                LOGGER.info("validating with openapi spec")
                # NOTE - don't change data (unmarshal) b/c we are downstream of data separation
                try:
                    # https://openapi-core.readthedocs.io/en/latest/validation.html
                    validate_request(reqhand.request, self.spec)  # type: ignore[arg-type]  # ->
                except Exception as e:
                    LOGGER.exception(f"Invalid request: {e}")
                    raise  # TODO - raise client-bound exception
                return await method(reqhand, *args, **kwargs)

            return wrapper

        return make_wrapper

    def write_and_validate(
        self,
        reqhand: RequestHandler,
        chunk: str | bytes | dict,
    ) -> None:
        """Validate the response and `write()`."""
        try:
            validate_response(reqhand.request, chunk, self.spec)  # type: ignore[arg-type]
        except Exception as e:
            LOGGER.exception(
                f"Response is not valid with openapi"
                f"{' (sending anyway)' if not self.testing else ''}"
                f": {e}"
            )
            if self.testing:
                raise
        reqhand.write(chunk)
