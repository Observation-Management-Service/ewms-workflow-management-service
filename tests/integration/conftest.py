"""conftest.py."""


import asyncio
import logging
import os
from typing import AsyncIterator

import pytest_asyncio

LOGGER = logging.getLogger(__name__)


@pytest_asyncio.fixture
async def startup_services() -> AsyncIterator[None]:
    """Startup REST server and database."""

    with open(os.environ["CI_MONGO_STDOUT"], "wb") as stdoutf, open(
        os.environ["CI_MONGO_STDERR"], "wb"
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

    with open(os.environ["CI_REST_STDOUT"], "wb") as stdoutf, open(
        os.environ["CI_REST_STDERR"], "wb"
    ) as stderrf:
        rest_task = asyncio.create_task(
            (
                await asyncio.create_subprocess_shell(
                    f"docker run --network='host' --rm {os.environ['CI_DOCKER_IMAGE_W_TAG']}",
                    stdout=stdoutf,
                    stderr=stderrf,
                )
            ).wait()
        )

    await asyncio.sleep(0)  # start up tasks

    yield

    mongo_task.cancel()
    rest_task.cancel()
