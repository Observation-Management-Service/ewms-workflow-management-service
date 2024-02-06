"""Mimic a TMS workflow, hitting the expected REST endpoints."""


from rest_tools.client import RestClient


async def test_000(rc: RestClient) -> None:
    """Regular workflow."""
    resp = await rc.request("GET", "/schema/openapi")
    # TODO - use openapi to validate response client-side (not done server side)
    print(resp)

    assert 0
