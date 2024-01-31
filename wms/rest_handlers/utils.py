"""Utils for REST routes."""


import logging

from openapi_core import OpenAPI  # type: ignore[attr-defined]
from tornado.web import RequestHandler

LOGGER = logging.getLogger(__name__)


def openapi_validate_request(spec: OpenAPI):  # type: ignore
    """Validate request obj against the given OpenAPI spec."""

    def make_wrapper(method):  # type: ignore[no-untyped-def]
        async def wrapper(self: RequestHandler, *args, **kwargs):  # type: ignore[no-untyped-def]
            LOGGER.info("validating with openapi spec")
            # NOTE - don't change data (unmarshal) b/c we are downstream of data separation
            try:
                # https://openapi-core.readthedocs.io/en/latest/validation.html
                spec.validate_request(self.request)  # ->
            except Exception as e:
                LOGGER.exception(f"Invalid request: {e}")
                raise  # TODO - raise client-bound exception
            return await method(self, *args, **kwargs)

        return wrapper

    return make_wrapper


def write_and_openapi_validate(
    self: RequestHandler,
    spec: OpenAPI,
    chunk: str | bytes | dict,
) -> None:
    """Validate the response and `write()`."""
    spec.validate_response(self.request, chunk)
    self.write(chunk)
