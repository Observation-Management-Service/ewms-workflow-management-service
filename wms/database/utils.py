"""utils.py."""

import copy
import logging
from urllib.parse import quote_plus

import jsonschema
from motor.motor_asyncio import AsyncIOMotorClient
from tornado import web

from ..config import ENV

LOGGER = logging.getLogger(__name__)


_DB_NAME = "WMS_DB"
WORKFLOWS_COLL_NAME = "WorkflowColl"
TASK_DIRECTIVES_COLL_NAME = "TaskDirectiveColl"
TASKFORCES_COLL_NAME = "TaskforceColl"


def get_jsonschema_spec_name(collection_name: str) -> str:
    """Map between the two naming schemes."""
    return collection_name.removesuffix("Coll")


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
    LOGGER.info("Ensuring indexes...")

    async def make_index(coll: str, attr: str, unique: bool = False) -> None:
        LOGGER.info(f"creating index for {coll=} {attr=} {unique=}...")
        await mongo_client[_DB_NAME][coll].create_index(  # type: ignore[index]
            attr,
            name=f"{attr.replace('.','_')}_index",
            unique=unique,
            background=True,
        )

    # WORKFLOWS
    await make_index(WORKFLOWS_COLL_NAME, "workflow_id", unique=True)
    await make_index(WORKFLOWS_COLL_NAME, "timestamp")
    await make_index(WORKFLOWS_COLL_NAME, "priority")

    # TASK_DIRECTIVES
    await make_index(TASK_DIRECTIVES_COLL_NAME, "task_id", unique=True)
    await make_index(TASK_DIRECTIVES_COLL_NAME, "workflow_id")
    await make_index(TASK_DIRECTIVES_COLL_NAME, "timestamp")

    # TASKFORCES
    await make_index(TASKFORCES_COLL_NAME, "taskforce_uuid", unique=True)
    await make_index(TASKFORCES_COLL_NAME, "task_id")
    await make_index(TASKFORCES_COLL_NAME, "workflow_id")
    await make_index(TASKFORCES_COLL_NAME, "phase")
    await make_index(TASKFORCES_COLL_NAME, "timestamp")
    await make_index(TASKFORCES_COLL_NAME, "priority")

    LOGGER.info("Ensured indexes (may continue in background).")


def _mongo_to_jsonschema_prep(
    og_dict: dict,
    og_schema: dict,
    allow_partial_update: bool,
) -> tuple[dict, dict]:
    """Converts a mongo-style dotted dict to a nested dict with an augmented schema.

    NOTE: Does not support array/list dot-indexing

    Example:
        in:
            {"book.title": "abc", "book.content": "def", "author": "ghi"}
            {
                "type": "object",
                "properties": {
                    "author": { "type": "string" },
                    "book": {
                        "type": "object",
                        "properties": { "content": { "type": "string" } },
                        "required": [<some>]
                    },
                    "copyright": {
                        "type": "object",
                        "properties": { ... },
                        "required": [<some>]
                    },
                    ...
                },
                "required": [<some>]
            }
        out:
            {"book": {"title": "abc", "content": "def"}, "author": "ghi"}
            {
                "type": "object",
                "properties": {
                    "author": { "type": "string" },
                    "book": {
                        "type": "object",
                        "properties": { "content": { "type": "string" } },
                        "required": []  # NONE!
                    },
                    "copyright": {
                        "type": "object",
                        "properties": { ... },
                        "required": [<some>]  # not changed b/c og_key was not seen in dot notation
                    },
                    ...
                },
                "required": []  # NONE!
            }
    """
    match (allow_partial_update, any("." in k for k in og_dict.keys())):
        # yes partial & yes dots -> proceed to rest of func
        case (True, True):
            schema = copy.deepcopy(og_schema)
            schema["required"] = []
        # yes partial & no dots -> quick exit
        case (True, False):
            schema = copy.deepcopy(og_schema)
            schema["required"] = []
            return og_dict, schema
        # no partial & yes dots -> error
        case (False, True):
            raise web.HTTPError(
                500,
                log_message="Partial updating disallowed but instance contains dotted parent_keys.",
                reason="Internal database schema validation error",
            )
        # no partial & no dots -> immediate exit
        case (False, False):
            return og_dict, og_schema
        # ???
        case _other:
            raise RuntimeError(f"Unknown match: {_other}")

    # https://stackoverflow.com/a/75734554/13156561 (looping logic)
    out = {}  # type: ignore
    for og_key, value in og_dict.items():
        if "." not in og_key:
            out[og_key] = value
            continue
        else:
            # (re)set cursors to root
            cursor = out
            schema_props_cursor = schema["properties"]
            # iterate & attach keys
            *parent_keys, leaf_key = og_key.split(".")
            for k in parent_keys:
                cursor = cursor.setdefault(k, {})
                # mark nested object 'required' as none
                if schema_props_cursor:
                    # ^^^ falsy when not "in" a properties obj, ex: parent only has 'additionalProperties'
                    schema_props_cursor[k]["required"] = []
                    schema_props_cursor = schema_props_cursor[k].get("properties")
            # place value
            cursor[leaf_key] = value
    return out, schema


def web_jsonschema_validate(
    instance: dict,
    schema: dict,
    allow_partial_update: bool = False,
) -> None:
    """Wrap `jsonschema.validate` with `web.HTTPError` (500)."""

    try:
        jsonschema.validate(
            *_mongo_to_jsonschema_prep(instance, schema, allow_partial_update)
        )
    except jsonschema.exceptions.ValidationError as e:
        LOGGER.exception(e)
        raise web.HTTPError(
            status_code=500,
            log_message=f"{e.__class__.__name__}: {e}",  # to stderr
            reason="Attempted to insert invalid data into database",  # to client
        )
