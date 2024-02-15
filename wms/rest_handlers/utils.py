"""Utils for REST routes."""


import logging

import openapi_core
import requests
import tornado
from openapi_core.contrib import requests as openapi_core_requests
from openapi_core.validation.exceptions import ValidationError
from openapi_core.validation.schemas.exceptions import InvalidSchemaValue
from tornado import web

from ..config import ENV

LOGGER = logging.getLogger(__name__)


def validate_request(openapi_spec: openapi_core.OpenAPI):  # type: ignore
    """Validate request obj against the given OpenAPI spec."""

    def make_wrapper(method):  # type: ignore[no-untyped-def]
        async def wrapper(zelf: web.RequestHandler, *args, **kwargs):  # type: ignore[no-untyped-def]
            LOGGER.info("validating with openapi spec")
            # NOTE - don't change data (unmarshal) b/c we are downstream of data separation
            try:
                # https://openapi-core.readthedocs.io/en/latest/validation.html
                openapi_spec.validate_request(
                    http_server_request_to_openapi_request(zelf.request),
                )
            except ValidationError as e:
                LOGGER.error(f"invalid request: {e.__class__.__name__} - {e}")
                if isinstance(e, InvalidSchemaValue):
                    reason = "; ".join(  # to client
                        # verbose details after newline
                        str(x).split("\n", maxsplit=1)[0]
                        for x in e.schema_errors
                    )
                else:
                    reason = str(e)  # to client
                if ENV.CI:  # in prod, don't fill up logs w/ traces from invalid data
                    LOGGER.exception(e)
                raise web.HTTPError(
                    status_code=400,
                    log_message=f"{e.__class__.__name__}: {e}",  # to stderr
                    reason=reason,  # to client
                )
            except Exception as e:
                LOGGER.error(f"unexpected exception: {e.__class__.__name__} - {e}")
                LOGGER.exception(e)
                raise web.HTTPError(
                    status_code=400,
                    log_message=f"{e.__class__.__name__}: {e}",  # to stderr
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
