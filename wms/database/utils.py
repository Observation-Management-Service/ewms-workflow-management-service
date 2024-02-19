"""utils.py."""


import logging
from typing import Any
from urllib.parse import quote_plus

import jsonschema
from motor.motor_asyncio import AsyncIOMotorClient
from tornado import web

from ..config import ENV

LOGGER = logging.getLogger(__name__)


_DB_NAME = "WMS_DB"
_TASK_DIRECTIVES_COLL_NAME = "TaskDirectives"
_TASKFORCES_COLL_NAME = "Taskforces"


async def create_mongodb_client() -> AsyncIOMotorClient:  # type: ignore[valid-type]
    """Construct the MongoDB client."""
    auth_user = quote_plus(ENV.MONGODB_AUTH_USER)
    auth_pass = quote_plus(ENV.MONGODB_AUTH_PASS)

    if auth_user and auth_pass:
        url = f"mongodb://{auth_user}:{auth_pass}@{ENV.MONGODB_HOST}:{ENV.MONGODB_PORT}"
    else:
        url = f"mongodb://{ENV.MONGODB_HOST}:{ENV.MONGODB_PORT}"

    mongo_client = AsyncIOMotorClient(url)  # type: ignore[var-annotated]
    return mongo_client


async def ensure_indexes(mongo_client: AsyncIOMotorClient) -> None:  # type: ignore[valid-type]
    """Create indexes in collections.

    Call on server startup.
    """

    for coll in [_TASK_DIRECTIVES_COLL_NAME, _TASKFORCES_COLL_NAME]:
        await mongo_client[_DB_NAME][coll].create_index(  # type: ignore[index]
            "task_id",
            name="task_id_index",
            unique=True,
        )

    await mongo_client[_DB_NAME][_TASKFORCES_COLL_NAME].create_index(  # type: ignore[index]
        "taskforce_uuid",
        name="taskforce_uuid_index",
        unique=True,
    )


def web_jsonschema_validate(instance: Any, schema: dict) -> None:
    """Wrap `jsonschema.validate` with `web.HTTPError` (500)."""
    try:
        jsonschema.validate(instance, schema)
    except jsonschema.exceptions.ValidationError as e:
        LOGGER.exception(e)
        raise web.HTTPError(
            status_code=500,
            log_message=f"{e.__class__.__name__}: {e}",  # to stderr
            reason="Attempted to insert invalid data into database",  # to client
        )


class DocumentNotFoundException(Exception):
    """Raised when document is not found for a particular query."""
