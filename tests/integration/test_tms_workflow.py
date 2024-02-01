"""Mimic a TMS workflow, hitting the expected REST endpoints."""


import asyncio


async def test_000(startup_services: None) -> None:
    """Regular workflow."""
    for i in range(100):
        print("Sleep 1")
        await asyncio.sleep(1)

    assert 0
