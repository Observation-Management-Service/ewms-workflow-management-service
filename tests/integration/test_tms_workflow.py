"""Mimic a TMS workflow, hitting the expected REST endpoints."""


from rest_tools.client import RestClient


async def test_000(rc: RestClient) -> None:
    """Regular workflow."""
    resp = await rc.request("GET", "/schema/openapi")
    print(resp)

    assert 0
