"""Utils for REST routes."""


import logging

import openapi_core
import requests
import tornado
from openapi_core.contrib import requests as openapi_core_requests
from tornado.web import RequestHandler

LOGGER = logging.getLogger(__name__)


class OpenAPIValidator:
    """A helper class for validating requests and responses with openapi."""

    def __init__(self, spec: openapi_core.Spec) -> None:
        self.spec = spec

    def validate_request(self):  # type: ignore
        """Validate request obj against the given OpenAPI spec."""

        def make_wrapper(method):  # type: ignore[no-untyped-def]
            async def wrapper(reqhand: RequestHandler, *args, **kwargs):  # type: ignore[no-untyped-def]
                LOGGER.info("validating with openapi spec")
                # NOTE - don't change data (unmarshal) b/c we are downstream of data separation
                try:
                    # https://openapi-core.readthedocs.io/en/latest/validation.html
                    openapi_core.validate_request(
                        http_server_request_to_openapi_request(reqhand.request),
                        self.spec,
                    )
                except Exception as e:
                    LOGGER.exception(f"Invalid request: {e}")
                    raise  # TODO - raise client-bound exception
                return await method(reqhand, *args, **kwargs)

            return wrapper

        return make_wrapper


def http_server_request_to_openapi_request(
    req: tornado.httputil.HTTPServerRequest,
) -> openapi_core_requests.RequestsOpenAPIRequest:
    """Convert a `tornado.httputil.HTTPServerRequest` to openapi's type."""
    return openapi_core_requests.RequestsOpenAPIRequest(
        requests.Request(
            method=req.method.lower() if req.method else "get",
            url=req.uri,
            headers=req.headers,
            files=req.files,
            data=req.body if not req.body_arguments else None,  # see below
            params=req.query_arguments,
            # auth=None,
            cookies=req.cookies,
            # hooks=None,
            json=req.body_arguments if req.body_arguments else None,  # see above
        )
    )
