"""conftest.py."""


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
    """Yield a RestClient."""
    yield RestClient(
        f'{os.environ["REST_HOST"]}:{os.environ["REST_PORT"]}',
        timeout=3,
        retries=2,
    )
