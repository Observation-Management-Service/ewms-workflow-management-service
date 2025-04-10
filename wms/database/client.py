"""Tools for interacting with the mongo database."""

import logging

from motor.motor_asyncio import AsyncIOMotorClient
from wipac_dev_tools.mongo_jsonschema_tools import (
    DocumentNotFoundException,
    MongoJSONSchemaValidatedCollection,
    MongoJSONSchemaValidationError,
)

from .utils import (
    TASKFORCES_COLL_NAME,
    TASK_DIRECTIVES_COLL_NAME,
    WORKFLOWS_COLL_NAME,
    _DB_NAME,
    get_jsonschema_spec_name,
)
from ..config import MONGO_COLLECTION_JSONSCHEMA_SPECS

__all__ = [  # export this one
    "DocumentNotFoundException",
    "MongoJSONSchemaValidationError",
]


class WMSMongoValidatedDatabase:
    """Wraps a MongoDB client and collection clients with json schema validation."""

    def __init__(
        self,
        mongo_client: AsyncIOMotorClient,
        parent_logger: logging.Logger | None = None,
    ):
        self.mongo_client = mongo_client
        self.workflows_collection = MongoJSONSchemaValidatedCollection(
            mongo_client[_DB_NAME][WORKFLOWS_COLL_NAME],
            MONGO_COLLECTION_JSONSCHEMA_SPECS[
                get_jsonschema_spec_name(WORKFLOWS_COLL_NAME)
            ],
            parent_logger,
        )
        self.task_directives_collection = MongoJSONSchemaValidatedCollection(
            mongo_client[_DB_NAME][TASK_DIRECTIVES_COLL_NAME],
            MONGO_COLLECTION_JSONSCHEMA_SPECS[
                get_jsonschema_spec_name(TASK_DIRECTIVES_COLL_NAME)
            ],
            parent_logger,
        )
        self.taskforces_collection = MongoJSONSchemaValidatedCollection(
            mongo_client[_DB_NAME][TASKFORCES_COLL_NAME],
            MONGO_COLLECTION_JSONSCHEMA_SPECS[
                get_jsonschema_spec_name(TASKFORCES_COLL_NAME)
            ],
            parent_logger,
        )
