"""Tools for interacting with the mongo database."""

import logging
from typing import Any, AsyncIterator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pymongo import ReturnDocument

from .utils import (
    TASKFORCES_COLL_NAME,
    TASK_DIRECTIVES_COLL_NAME,
    WORKFLOWS_COLL_NAME,
    _DB_NAME,
    get_jsonschema_spec_name,
    web_jsonschema_validate,
)
from ..config import MONGO_COLLECTION_JSONSCHEMA_SPECS


class WMSMongoValidatedDatabase:
    """Wraps a MongoDB client and collection clients with json schema validation."""

    def __init__(
        self,
        mongo_client: AsyncIOMotorClient,
        parent_logger: logging.Logger | None = None,
    ):
        self.mongo_client = mongo_client
        self.workflows_collection = MongoValidatedCollection(
            mongo_client,
            WORKFLOWS_COLL_NAME,
            parent_logger,
        )
        self.task_directives_collection = MongoValidatedCollection(
            mongo_client,
            TASK_DIRECTIVES_COLL_NAME,
            parent_logger,
        )
        self.taskforces_collection = MongoValidatedCollection(
            mongo_client,
            TASKFORCES_COLL_NAME,
            parent_logger,
        )


class DocumentNotFoundException(Exception):
    """Raised when document is not found for a particular query."""


class MongoValidatedCollection:
    """For interacting with a mongo collection using json schema validation."""

    def __init__(
        self,
        mongo_client: AsyncIOMotorClient,  # type: ignore[valid-type]
        collection_name: str,
        parent_logger: logging.Logger | None = None,
    ) -> None:
        self._collection = AsyncIOMotorCollection(  # type: ignore[var-annotated]
            mongo_client[_DB_NAME],  # type: ignore[arg-type]
            collection_name,
        )
        self._schema = MONGO_COLLECTION_JSONSCHEMA_SPECS[
            get_jsonschema_spec_name(collection_name)
        ]

        if parent_logger is not None:
            self.logger = logging.getLogger(
                f"{parent_logger.name}.db.{collection_name.lower()}"
            )
        else:
            self.logger = logging.getLogger(f"{__name__}.{collection_name.lower()}")

    ####################################################################
    # WRITES
    ####################################################################

    def _web_jsonschema_validate_mongo_update(self, update: dict[str, Any]) -> None:
        """Validate the data for each given mongo-syntax update operator."""
        for operator in update:
            match operator:
                case "$set":
                    web_jsonschema_validate(
                        update[operator], self._schema, allow_partial_update=True
                    )
                case "$push":
                    web_jsonschema_validate(
                        # validate each value as if it was the whole field's list -- other wise `str != [str]`
                        {k: [v] for k, v in update[operator].items()},
                        self._schema,
                        allow_partial_update=True,
                    )
                # FUTURE: insert more operators here
                case other:
                    raise KeyError(f"Unsupported mongo-syntax update operator: {other}")

    async def insert_one(self, doc: dict, **kwargs: Any) -> dict:
        """Insert the doc (dict)."""
        self.logger.debug(f"inserting one: {doc}")

        web_jsonschema_validate(doc, self._schema)
        await self._collection.insert_one(doc, **kwargs)
        # https://pymongo.readthedocs.io/en/stable/faq.html#writes-and-ids
        doc.pop("_id")

        self.logger.debug(f"inserted one: {doc}")
        return doc

    async def find_one_and_update(
        self,
        query: dict,
        update: dict,
        **kwargs: Any,
    ) -> dict:
        """Update the doc and return updated doc."""
        self.logger.debug(f"update one with query: {query}")

        self._web_jsonschema_validate_mongo_update(update)
        doc = await self._collection.find_one_and_update(
            query,
            update,
            return_document=ReturnDocument.AFTER,
            **kwargs,
        )
        if not doc:
            raise DocumentNotFoundException()

        self.logger.debug(f"updated one ({query}): {doc}")
        return doc  # type: ignore[no-any-return]

    async def insert_many(self, docs: list[dict], **kwargs: Any) -> list[dict]:
        """Insert multiple docs."""
        self.logger.debug(f"inserting many: {docs}")

        for doc in docs:
            web_jsonschema_validate(doc, self._schema)

        await self._collection.insert_many(docs, **kwargs)
        # https://pymongo.readthedocs.io/en/stable/faq.html#writes-and-ids
        for doc in docs:
            doc.pop("_id")

        self.logger.debug(f"inserted many: {docs}")
        return docs

    async def update_many(
        self,
        query: dict,
        update: dict,
        **kwargs: Any,
    ) -> int:
        """Update all matching docs."""
        self.logger.debug(f"update many with query: {query}")

        self._web_jsonschema_validate_mongo_update(update)
        res = await self._collection.update_many(query, update, **kwargs)
        if not res.matched_count:
            raise DocumentNotFoundException()

        self.logger.debug(f"updated many: {query}")
        return res.modified_count

    ####################################################################
    # READS
    ####################################################################

    async def find_one(self, query: dict, **kwargs: Any) -> dict:
        """Find one matching the query."""
        self.logger.debug(f"finding one with query: {query}")

        doc = await self._collection.find_one(query, **kwargs)
        if not doc:
            raise DocumentNotFoundException()
        # https://pymongo.readthedocs.io/en/stable/faq.html#writes-and-ids
        doc.pop("_id")

        self.logger.debug(f"found one: {doc}")
        return doc  # type: ignore[no-any-return]

    async def find_all(
        self,
        query: dict,
        projection: list,
        **kwargs: Any,
    ) -> AsyncIterator[dict]:
        """Find all matching the query."""
        self.logger.debug(f"finding with query: {query}")

        doc = {}
        async for doc in self._collection.find(query, projection, **kwargs):
            # https://pymongo.readthedocs.io/en/stable/faq.html#writes-and-ids
            doc.pop("_id")
            self.logger.debug(f"found {doc}")
            yield doc

        if not doc:
            self.logger.debug(f"found nothing matching query: {query}")
