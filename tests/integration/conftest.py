"""conftest.py."""


import logging
import os
from typing import AsyncIterator

import pytest_asyncio
from rest_tools.client import RestClient

LOGGER = logging.getLogger(__name__)


@pytest_asyncio.fixture
async def rc() -> AsyncIterator[RestClient]:
    """Yield a RestClient."""
    yield RestClient(
        f'http://{os.environ["REST_HOST"]}:{os.environ["REST_PORT"]}',
        timeout=3,
        retries=2,
    )
