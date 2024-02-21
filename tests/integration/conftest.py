"""conftest.py."""


import logging
import os
from typing import AsyncIterator

import pytest_asyncio
from pymongo import MongoClient
from rest_tools.client import RestClient

LOGGER = logging.getLogger(__name__)


@pytest_asyncio.fixture
async def rc() -> AsyncIterator[RestClient]:
    """Yield a RestClient."""
    mongo_client = MongoClient(
        f"mongodb://{os.environ['MONGODB_HOST']}:{os.environ['MONGODB_PORT']}"
    )

    # make sure db is empty
    assert not mongo_client.list_database_names()

    # connect rc
    yield RestClient(
        f'http://{os.environ["REST_HOST"]}:{os.environ["REST_PORT"]}',
        timeout=3,
        retries=2,
    )

    # clean up database
    for db in mongo_client.list_database_names():
        mongo_client.drop_database(db)
