"""utils.py."""


import logging
from typing import Any

import openapi_core
import requests
from openapi_core.contrib import requests as openapi_core_requests
from rest_tools.client import RestClient

LOGGER = logging.getLogger(__name__)


def request_and_validate(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    method: str,
    path: str,
    args: dict[str, Any] | None = None,
) -> Any:
    """Make request and validate the response."""
    url, kwargs = rc._prepare(method, path, args=args)
    response = requests.request(method, url, **kwargs)

    # duck typing magic
    class _DuckResponse(openapi_core.protocols.Response):
        """AKA 'openapi_core_requests.RequestsOpenAPIResponse' but correct."""

        @property
        def data(self) -> bytes | None:
            return response.content

        @property
        def status_code(self) -> int:
            return int(response.status_code)

        @property
        def content_type(self) -> str:
            # application/json; charset=UTF-8  ->  application/json
            # ex: openapi_core.validation.response.exceptions.DataValidationError: DataValidationError: Content for the following mimetype not found: application/json; charset=UTF-8. Valid mimetypes: ['application/json']
            return str(response.headers.get("Content-Type", "")).split(";")[0]
            # alternatively, look at how 'openapi_core_requests.RequestsOpenAPIRequest.mimetype' handles similarly

        @property
        def headers(self) -> dict:
            return dict(response.headers)

    openapi_spec.validate_response(
        openapi_core_requests.RequestsOpenAPIRequest(response.request),
        _DuckResponse(),
    )

    out = rc._decode(response.content)
    response.raise_for_status()
    if path != "/schema/openapi":
        print(out)
    return out
