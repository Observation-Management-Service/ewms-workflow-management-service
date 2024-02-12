"""Utils for REST routes."""


import logging

import openapi_core
import requests
import tornado
from openapi_core.contrib import requests as openapi_core_requests
from openapi_core.validation.request.exceptions import InvalidRequestBody
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue
from tornado import web

LOGGER = logging.getLogger(__name__)


class OpenAPIValidator:
    """A helper class for validating requests and responses with openapi."""

    def __init__(self, spec: openapi_core.Spec) -> None:
        self.spec = spec

    def validate_request(self):  # type: ignore
        """Validate request obj against the given OpenAPI spec."""

        def make_wrapper(method):  # type: ignore[no-untyped-def]
            async def wrapper(reqhand: web.RequestHandler, *args, **kwargs):  # type: ignore[no-untyped-def]
                LOGGER.info("validating with openapi spec")
                # NOTE - don't change data (unmarshal) b/c we are downstream of data separation
                try:
                    # https://openapi-core.readthedocs.io/en/latest/validation.html
                    openapi_core.validate_request(
                        http_server_request_to_openapi_request(reqhand.request),
                        self.spec,
                    )
                except Exception as e:
                    LOGGER.error(f"Invalid request: {e}")
                    if isinstance(e, InvalidRequestBody) and isinstance(
                        e.__context__, InvalidSchemaValue
                    ):
                        LOGGER.error(f"-> {e.__context__}")
                        reason = "; ".join(  # to client
                            str(x).replace("\n", "")  # newlines not http allowed
                            for x in e.__context__.schema_errors
                        )
                        raise web.HTTPError(
                            status_code=400,
                            log_message=reason,  # to stderr
                            reason=reason,  # to client
                        )
                    else:
                        raise web.HTTPError(
                            status_code=400,
                            log_message=str(e),
                        )
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
            url=f"{req.protocol}://{req.host}{req.uri}",
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
