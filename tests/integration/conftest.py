"""conftest.py."""


import asyncio
import itertools
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
                    (
                        f"docker run --network='host' --rm "
                        f"{os.environ['CI_DOCKER_IMAGE_W_TAG']}"
                        # forward all env vars
                        f" {' --env '.join(f'{k}={v}' for k,v in os.environ.items())}"
                    ),
                    stdout=stdoutf,
                    stderr=stderrf,
                )
            ).wait()
        )

    await asyncio.sleep(0)  # start up tasks

    # ping until all live
    for hostname in [
        f'{os.environ["MONGODB_HOST"]}:{os.environ["MONGODB_PORT"]}',
        f'{os.environ["REST_HOST"]}:{os.environ["REST_PORT"]}',
    ]:
        LOGGER.info(f"waiting for host: {hostname}")
        for i in itertools.count():
            if i > 60:
                LOGGER.critical(f"could not connect to {hostname}")
                break
            if os.system("ping -c 1 " + hostname) == 0:
                break
            LOGGER.info(f"{hostname}...")
            await asyncio.sleep(1)
        LOGGER.info(f"reached host: {hostname}")

    yield

    mongo_task.cancel()
    rest_task.cancel()
