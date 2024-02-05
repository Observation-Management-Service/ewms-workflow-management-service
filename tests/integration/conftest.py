"""conftest.py."""


import asyncio
import dataclasses
import itertools
import logging
import os
from typing import AsyncIterator

import pytest_asyncio
from wms import config  # only use to access constants

LOGGER = logging.getLogger(__name__)


FORWARD_ENVVARS = [
    f.name for f in dataclasses.fields(config.EnvConfig) if f.name in os.environ
]


@pytest_asyncio.fixture
async def startup_services() -> AsyncIterator[None]:
    """Startup REST server and database."""

    with open(os.environ["CI_MONGO_STDOUT"], "wb") as stdoutf, open(
        os.environ["CI_MONGO_STDERR"], "wb"
    ) as stderrf:
        cmd = "docker run --network='host' --rm bitnami/mongodb:4"
        LOGGER.info(f"running: {cmd}")
        mongo_task = asyncio.create_task(
            (
                await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=stdoutf,
                    stderr=stderrf,
                )
            ).wait()
        )

    with open(os.environ["CI_REST_STDOUT"], "wb") as stdoutf, open(
        os.environ["CI_REST_STDERR"], "wb"
    ) as stderrf:
        cmd = (
            f"docker run --network='host' --rm "
            f"{os.environ['CI_DOCKER_IMAGE_W_TAG']}"
            # forward all env vars
            f""" {' '.join(f'--env {k}="{os.environ[k]}"' for k in FORWARD_ENVVARS)}"""
        )
        LOGGER.info(f"running: {cmd}")
        rest_task = asyncio.create_task(
            (
                await asyncio.create_subprocess_shell(
                    cmd,
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
                LOGGER.info(f"reached host: {hostname}")
                break
            LOGGER.info(f"{hostname}...")
            await asyncio.sleep(1)

    yield

    mongo_task.cancel()
    rest_task.cancel()
