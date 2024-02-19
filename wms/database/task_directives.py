"""Interface to task directive collection in the mongo database."""


import logging
from typing import AsyncIterator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from ..config import DB_JSONSCHEMA_SPECS
from .utils import (
    _DB_NAME,
    _TASK_DIRECTIVES_COLL_NAME,
    DocumentNotFoundException,
    web_jsonschema_validate,
)

LOGGER = logging.getLogger(__name__)


class TaskDirectiveMongoClient:
    """A client for interacting with task directives."""

    def __init__(self, mongo_client: AsyncIOMotorClient) -> None:  # type: ignore[valid-type]
        self.collection = AsyncIOMotorCollection(
            mongo_client[_DB_NAME], _TASK_DIRECTIVES_COLL_NAME  # type: ignore[index]
        )
        self.schema = DB_JSONSCHEMA_SPECS["TaskDirective"]

    async def insert(self, task_directive: dict) -> dict:
        """Insert the task_directive dict."""
        LOGGER.debug(f"inserting task_directive: {task_directive}")

        web_jsonschema_validate(task_directive, self.schema)
        await self.collection.insert_one(task_directive)
        # https://pymongo.readthedocs.io/en/stable/faq.html#writes-and-ids
        task_directive.pop("_id")

        LOGGER.debug(f"inserted task_directive: {task_directive}")
        return task_directive

    async def find_one(self, query: dict) -> dict:
        """Find one task_directive dict."""
        LOGGER.debug(f"finding one with query: {query}")

        doc = await self.collection.find_one(query)
        if not doc:
            raise DocumentNotFoundException()
        # https://pymongo.readthedocs.io/en/stable/faq.html#writes-and-ids
        doc.pop("_id")

        LOGGER.debug(f"found {doc}")
        return doc  # type: ignore[no-any-return]

    async def find(self, query: dict, projection: dict) -> AsyncIterator[dict]:
        """Find all matching task_directive dict."""
        LOGGER.debug(f"finding with query: {query}")

        doc = {}
        async for doc in self.collection.find(query, projection):
            # https://pymongo.readthedocs.io/en/stable/faq.html#writes-and-ids
            doc.pop("_id")
            LOGGER.debug(f"found {doc}")
            yield doc

        if not doc:
            LOGGER.debug(f"found nothing matching query: {query}")
