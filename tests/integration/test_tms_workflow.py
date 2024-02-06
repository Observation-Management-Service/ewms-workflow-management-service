"""Mimic a TMS workflow, hitting the expected REST endpoints."""


import json
from pathlib import Path

import openapi_core
import requests
from openapi_core.contrib import requests as openapi_core_requests
from rest_tools.client import RestClient

_OPENAPI_JSON = Path(__file__).parent / "../../wms/schema/rest_openapi.json"
_OPENAPI_SPEC = openapi_core.Spec.from_file_path(str(_OPENAPI_JSON))


def validate_response(response: requests.Response) -> None:
    """Validate using 'requests' types."""

    # duck typing magic
    openapi_resp = openapi_core_requests.RequestsOpenAPIResponse(response)
    openapi_resp.headers = dict(openapi_resp.headers)

    openapi_core.validate_response(
        openapi_core_requests.RequestsOpenAPIRequest(response.request),
        openapi_resp,  # type: ignore[arg-type]
        _OPENAPI_SPEC,
    )


async def test_000(rc: RestClient) -> None:
    """Regular workflow."""
    resp: requests.Response = requests.get(rc.address + "/schema/openapi")
    # TODO - use openapi to validate response client-side (not done server side)
    print(resp)
    with open(_OPENAPI_JSON, "rb") as f:
        assert json.load(f) == rc._decode(resp.content)
    validate_response(resp)
