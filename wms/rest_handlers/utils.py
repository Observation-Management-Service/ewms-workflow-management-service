"""Utils for REST routes."""


import logging

import openapi_core
import requests
import tornado
from openapi_core.contrib import requests as openapi_core_requests
from openapi_core.validation.exceptions import ValidationError
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
            async def wrapper(zelf: web.RequestHandler, *args, **kwargs):  # type: ignore[no-untyped-def]
                LOGGER.info("validating with openapi spec")
                # NOTE - don't change data (unmarshal) b/c we are downstream of data separation
                try:
                    # https://openapi-core.readthedocs.io/en/latest/validation.html
                    openapi_core.validate_request(
                        http_server_request_to_openapi_request(zelf.request),
                        self.spec,
                    )
                except ValidationError as e:
                    LOGGER.error(f"invalid request: {e.__class__.__name__} - {e}")
                    if isinstance(e, InvalidRequestBody) and isinstance(
                        e.__context__, InvalidSchemaValue
                    ):
                        LOGGER.error(f"-> {e.__context__}")
                        reason = "; ".join(  # to client
                            # verbose details after newline
                            str(x).split("\n", maxsplit=1)[0]
                            for x in e.__context__.schema_errors
                        )
                    else:
                        reason = str(e)  # to client
                    raise web.HTTPError(
                        status_code=400,
                        log_message=str(e),  # to stderr
                        reason=reason,  # to client
                    )
                except Exception as e:
                    LOGGER.error(f"unexpected exception: {e.__class__.__name__} - {e}")
                    raise web.HTTPError(
                        status_code=400,
                        log_message=str(e),  # to stderr
                        reason=None,  # to client (don't send possibly sensitive info)
                    )

                return await method(zelf, *args, **kwargs)

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
