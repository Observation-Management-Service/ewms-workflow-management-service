"""conftest.py."""


import asyncio
import dataclasses
import logging
import os
from typing import AsyncIterator

import pytest_asyncio
from rest_tools.client import RestClient
from wms import config  # only use to access constants

LOGGER = logging.getLogger(__name__)


FORWARD_ENVVARS = [
    f.name for f in dataclasses.fields(config.EnvConfig) if f.name in os.environ
]


@pytest_asyncio.fixture
async def rc() -> AsyncIterator[RestClient]:
    """Startup REST server and database, then yield a RestClient.

    Cleanup when iterator resumes.
    """
    with open(os.environ["CI_REST_STDOUT"], "wb") as stdoutf, open(
        os.environ["CI_REST_STDERR"], "wb"
    ) as stderrf:
        cmd = (
            f"docker run --network='host' --rm "
            # forward all env vars
            f""" {' '.join(f'--env {k}="{os.environ[k]}"' for k in FORWARD_ENVVARS)}"""
            f" {os.environ['CI_DOCKER_IMAGE_W_TAG']}"
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

    yield RestClient(
        f'{os.environ["REST_HOST"]}:{os.environ["REST_PORT"]}',
        timeout=3,
        retries=2,
    )

    rest_task.cancel()
