"""Mimic a TMS workflow, hitting the expected REST endpoints."""


import json
from pathlib import Path

from rest_tools.client import RestClient


async def test_000(rc: RestClient) -> None:
    """Regular workflow."""
    resp = await rc.request("GET", "/schema/openapi")
    # TODO - use openapi to validate response client-side (not done server side)
    print(resp)
    with open(Path(__file__).parent / "../../wms/schema/rest_openapi.json", "rb") as f:
        assert json.load(f) == resp

    assert 0
