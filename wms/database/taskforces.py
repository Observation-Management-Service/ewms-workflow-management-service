"""Interface to the taskforces collection in the mongo database."""


import copy
import logging
from typing import AsyncIterator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from ..config import DB_JSONSCHEMA_SPECS
from .utils import (
    _DB_NAME,
    _TASKFORCES_COLL_NAME,
    DocumentNotFoundException,
    web_jsonschema_validate,
)

LOGGER = logging.getLogger(__name__)


class TaskforcesMongoClient:
    """A client for interacting with taskforce objects."""

    def __init__(self, mongo_client: AsyncIOMotorClient) -> None:  # type: ignore[valid-type]
        self.collection = AsyncIOMotorCollection(
            mongo_client[_DB_NAME], _TASKFORCES_COLL_NAME  # type: ignore[index]
        )
        self.schema = DB_JSONSCHEMA_SPECS["Taskforce"]

        # like schema, but for partial updates
        self._schema_partial = copy.deepcopy(self.schema)
        self._schema_partial["required"] = []

    async def insert(self, taskforce: dict) -> dict:
        """Insert the taskforce dict."""
        LOGGER.debug(f"inserting taskforce: {taskforce}")

        web_jsonschema_validate(taskforce, self.schema)
        await self.collection.insert_one(taskforce)
        # https://pymongo.readthedocs.io/en/stable/faq.html#writes-and-ids
        taskforce.pop("_id")

        LOGGER.debug(f"inserted taskforce: {taskforce}")
        return taskforce

    async def update_set_one(self, query: dict, set_update: dict) -> dict:
        """Update the taskforce obj."""
        LOGGER.debug(f"update one with query: {query}")

        web_jsonschema_validate(set_update, self._schema_partial)
        res = await self.collection.update_one(query, {"$set": set_update})

        LOGGER.debug(f"updated: {query}")
        return vars(res)

    async def find_one(self, query: dict) -> dict:
        """Find one taskforce dict."""
        LOGGER.debug(f"finding one with query: {query}")

        doc = await self.collection.find_one(query)
        if not doc:
            raise DocumentNotFoundException()
        # https://pymongo.readthedocs.io/en/stable/faq.html#writes-and-ids
        doc.pop("_id")

        LOGGER.debug(f"found {doc}")
        return doc  # type: ignore[no-any-return]

    async def find(self, query: dict, projection: dict) -> AsyncIterator[dict]:
        """Find all matching taskforce dict."""
        LOGGER.debug(f"finding with query: {query}")

        doc = {}
        async for doc in self.collection.find(query, projection):
            # https://pymongo.readthedocs.io/en/stable/faq.html#writes-and-ids
            doc.pop("_id")
            LOGGER.debug(f"found {doc}")
            yield doc

        if not doc:
            LOGGER.debug(f"found nothing matching query: {query}")
