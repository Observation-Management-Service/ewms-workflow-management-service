"""Tools for interacting with the mongo database."""

import copy
import logging
from typing import Any

import jsonschema
from motor.motor_asyncio import AsyncIOMotorClient
from tornado import web
from wipac_dev_tools.mongo_jsonschema_tools import (
    DocumentNotFoundException,
    IllegalDotsNotationActionException,
    MongoJSONSchemaValidatedCollection,
)

from ..config import OPENAPI_DICT
from .utils import (
    _DB_NAME,
    TASK_DIRECTIVES_COLL_NAME,
    TASKFORCES_COLL_NAME,
    WORKFLOWS_COLL_NAME,
)

__all__ = [  # export
    "DocumentNotFoundException",
]


def get_jsonschema_subspec_from_openapi(object_name: str) -> dict[str, Any]:
    """Get a deep-copy of the JSONSchema spec for an 'component.schemas' object.

    Makes all root fields required.
    """
    try:
        subspec = copy.deepcopy(OPENAPI_DICT["components"]["schemas"][object_name])
    except KeyError as e:
        raise ValueError(f"no JSONSchema spec found: {object_name}") from e

    subspec["required"] = list(subspec["properties"].keys())
    return subspec


def _validation_exception_callback(exc: Exception) -> Exception:
    """Translate exceptions for web use."""
    match exc:
        case jsonschema.exceptions.ValidationError():
            return web.HTTPError(
                status_code=500,
                log_message=f"{exc.__class__.__name__}: {exc}",  # to stderr
                reason="Attempted to insert invalid data into database",  # to client
            )
        case IllegalDotsNotationActionException():
            return web.HTTPError(
                status_code=500,
                log_message=f"{exc.__class__.__name__}: {exc}",  # to stderr
                reason="Could not perform action on database with provided syntax",  # to client
            )
        case _:
            return exc


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
            get_jsonschema_subspec_from_openapi(
                WORKFLOWS_COLL_NAME.removesuffix("Coll") + "Object",
            ),
            parent_logger,
            validation_exception_callback=_validation_exception_callback,
        )
        self.task_directives_collection = MongoJSONSchemaValidatedCollection(
            mongo_client[_DB_NAME][TASK_DIRECTIVES_COLL_NAME],
            get_jsonschema_subspec_from_openapi(
                TASK_DIRECTIVES_COLL_NAME.removesuffix("Coll") + "Object",
            ),
            parent_logger,
            validation_exception_callback=_validation_exception_callback,
        )
        self.taskforces_collection = MongoJSONSchemaValidatedCollection(
            mongo_client[_DB_NAME][TASKFORCES_COLL_NAME],
            get_jsonschema_subspec_from_openapi(
                TASKFORCES_COLL_NAME.removesuffix("Coll") + "Object",
            ),
            parent_logger,
            validation_exception_callback=_validation_exception_callback,
        )
