"""conftest.py."""


import asyncio
import logging
from typing import AsyncIterator

import pytest_asyncio

LOGGER = logging.getLogger(__name__)


@pytest_asyncio.fixture
async def startup_services() -> AsyncIterator[None]:
    """Startup REST server and database."""

    with open("mongodb.stdout", "wb") as stdoutf, open(
        "mongodb.stderr", "wb"
    ) as stderrf:
        mongo_task = asyncio.create_task(
            (
                await asyncio.create_subprocess_shell(
                    "docker run --network='host' --rm bitnami/mongodb:4",
                    stdout=stdoutf,
                    stderr=stderrf,
                )
            ).wait()
        )

    with open("rest.stdout", "wb") as stdoutf, open("rest.stderr", "wb") as stderrf:
        rest_task = asyncio.create_task(
            (
                await asyncio.create_subprocess_shell(
                    "docker run --network='host' --rm rest_local",
                    stdout=stdoutf,
                    stderr=stderrf,
                )
            ).wait()
        )

    await asyncio.sleep(0)  # start up tasks

    yield

    mongo_task.cancel()
    rest_task.cancel()
