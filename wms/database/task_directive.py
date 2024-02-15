"""Interface to task directive collection in the mongo database."""


import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from ..config import DB_JSONSCHEMA_SPECS
from .utils import (
    _DB_NAME,
    _TASK_DIRECTIVES_COLL_NAME,
    log_in_out,
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

    @log_in_out(LOGGER)  # type: ignore[misc]
    async def insert(self, task_directive: dict) -> dict:
        """Insert the task_directive dict."""
        web_jsonschema_validate(task_directive, self.schema)
        await self.collection.insert_one(task_directive)
        # https://pymongo.readthedocs.io/en/stable/faq.html#writes-and-ids
        task_directive.pop("_id")
        return task_directive
