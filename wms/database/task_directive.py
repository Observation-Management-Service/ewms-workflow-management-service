"""Interface to task directive collection in the mongo database."""


import logging

import jsonschema
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from ..config import DB_TASK_DIRECTIVE_SPEC
from .utils import _DB_NAME, _TASK_DIRECTIVES_COLL_NAME, log_in_out

LOGGER = logging.getLogger(__name__)


class TaskDirectiveMongoClient:
    """A client for interacting with task directives."""

    def __init__(self, mongo_client: AsyncIOMotorClient) -> None:  # type: ignore[valid-type]
        self.collection = AsyncIOMotorCollection(
            mongo_client[_DB_NAME], _TASK_DIRECTIVES_COLL_NAME  # type: ignore[index]
        )
        self.validator = DB_TASK_DIRECTIVE_SPEC

    @log_in_out(LOGGER)  # type: ignore[misc]
    async def insert(self, task_directive: dict) -> str:
        """Insert the task_directive dict."""
        jsonschema.validate(task_directive, self.validator)
        res = await self.collection.insert_one(task_directive)
        return repr(res)
