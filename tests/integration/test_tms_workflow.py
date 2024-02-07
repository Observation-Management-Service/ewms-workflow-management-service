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
    """Make request and validate the response."""
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
            # alternatively, look at how 'openapi_core_requests.RequestsOpenAPIRequest.mimetype' handles similarly

        @property
        def headers(self) -> dict:
            return dict(response.headers)

    openapi_core.validate_response(
        openapi_core_requests.RequestsOpenAPIRequest(response.request),
        _DuckResponse(),
        _OPENAPI_SPEC,
    )

    out = rc._decode(response.content)
    print(out)
    return out


async def test_000(rc: RestClient) -> None:
    """Regular workflow."""
    resp = request_and_validate(rc, "GET", "/schema/openapi")
    with open(_OPENAPI_JSON, "rb") as f:
        assert json.load(f) == resp

    #
    # USER...
    #

    task_directive = request_and_validate(
        rc,
        "POST",
        "/task/directive",
        {"foo": 1, "bar": 2},
    )

    resp = request_and_validate(
        rc,
        "GET",
        f"/task/directive/{task_directive['task_id']}",
    )
    assert resp == task_directive

    resp = request_and_validate(
        rc,
        "POST",
        "/task/directives/find",
        {"foo": 1, "bar": 2},
    )
    assert len(resp["tasks"]) == 1
    assert resp["tasks"][0] == task_directive

    #
    # TMS...
    #

    #
    # USER...
    #
