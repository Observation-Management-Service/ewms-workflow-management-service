"""Mimic a TMS workflow, hitting the expected REST endpoints."""


import json
from pathlib import Path
from typing import Any

import openapi_core
import requests
from openapi_core.contrib import requests as openapi_core_requests
from rest_tools.client import RestClient

_OPENAPI_JSON = Path(__file__).parent / "../../wms/schema/rest_openapi.json"
_OPENAPI_SPEC = openapi_core.Spec.from_file_path(str(_OPENAPI_JSON))


def request_and_validate(
    rc: RestClient,
    method: str,
    path: str,
    args: dict[str, Any] | None = None,
) -> Any:
    """Validate using 'requests' types."""
    url, kwargs = rc._prepare(method, path, args=args)
    response = requests.request(method, url, **kwargs)

    # duck typing magic
    class _DuckResponse(openapi_core.protocols.Response):
        """AKA 'openapi_core_requests.RequestsOpenAPIResponse' but correct."""

        @property
        def data(self) -> str:
            return response.content.decode("utf-8")

        @property
        def status_code(self) -> int:
            return int(response.status_code)

        @property
        def mimetype(self) -> str:
            # application/json; charset=UTF-8  ->  application/json
            # ex: openapi_core.validation.response.exceptions.DataValidationError: DataValidationError: Content for the following mimetype not found: application/json; charset=UTF-8. Valid mimetypes: ['application/json']
            return str(response.headers.get("Content-Type", "")).split(";")[0]

        @property
        def headers(self) -> dict:
            return dict(response.headers)

    openapi_core.validate_response(
        openapi_core_requests.RequestsOpenAPIRequest(response.request),
        _DuckResponse(),
        _OPENAPI_SPEC,
    )

    return rc._decode(response.content)


async def test_000(rc: RestClient) -> None:
    """Regular workflow."""
    resp = request_and_validate(rc, "GET", "/schema/openapi")
    print(resp)
    with open(_OPENAPI_JSON, "rb") as f:
        assert json.load(f) == resp
