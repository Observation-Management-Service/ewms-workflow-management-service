"""conftest.py."""


import logging
import os
from typing import AsyncIterator

import pytest_asyncio
from pymongo import MongoClient
from rest_tools.client import RestClient

LOGGER = logging.getLogger(__name__)
logging.getLogger("parse").setLevel(logging.INFO)


@pytest_asyncio.fixture
async def rc() -> AsyncIterator[RestClient]:
    """Yield a RestClient."""
    mongo_client = MongoClient(  # type: ignore[var-annotated]
        f"mongodb://{os.environ['MONGODB_HOST']}:{os.environ['MONGODB_PORT']}"
    )

    # make sure custom dbs' collections are empty
    for db in mongo_client.list_database_names():
        if db not in ["admin", "config", "local"]:
            for coll in mongo_client[db].list_collection_names():
                mongo_client[db][coll].delete_many({})

    # connect rc
    yield RestClient(
        f'http://{os.environ["REST_HOST"]}:{os.environ["REST_PORT"]}',
        timeout=3,
        retries=2,
    )
