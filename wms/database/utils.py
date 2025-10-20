"""utils.py."""

import json
import logging
from urllib.parse import quote_plus

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from wipac_dev_tools.mongo_jsonschema_tools import MongoJSONSchemaValidatedCollection

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

    async def make_index(
        coll: str,
        keys: str | list[tuple[str, int]],
        unique: bool = False,
    ) -> None:
        LOGGER.info(f"creating index for {coll=} {keys=} {unique=}...")
        index_name = (
            keys.replace(".", "_") + "_index"
            if isinstance(keys, str)
            else "_".join(k for k, _ in keys) + "_compound_index"
        )
        await mongo_client[_DB_NAME][coll].create_index(  # type: ignore[index]
            keys,
            name=index_name,
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
    await make_index(TASKFORCES_COLL_NAME, "cluster_id")  # can be None
    await make_index(TASKFORCES_COLL_NAME, "phase")
    await make_index(TASKFORCES_COLL_NAME, "timestamp")
    await make_index(TASKFORCES_COLL_NAME, "priority")
    await make_index(TASKFORCES_COLL_NAME, "job_event_log_fpath")
    await make_index(TASKFORCES_COLL_NAME, "schedd")
    # -- speed up TMS's request queries for '.../query/taskforces' -- new tfs
    await make_index(
        TASKFORCES_COLL_NAME,
        [
            ("schedd", ASCENDING),
            ("job_event_log_fpath", ASCENDING),
            ("timestamp", ASCENDING),
        ],
    )
    # -- speed up TMS's request queries for '.../query/taskforces' -- completed tfs
    await make_index(
        TASKFORCES_COLL_NAME,
        [
            ("schedd", ASCENDING),
            ("job_event_log_fpath", ASCENDING),
            ("phase", ASCENDING),
        ],
    )

    LOGGER.info("Ensured indexes (may continue in background).")


async def paginated_find_all(
    query: dict,
    after: str | None,
    projection: list,
    coll: MongoJSONSchemaValidatedCollection,
) -> tuple[list, str | None]:
    """
    Handle paginated queries to the database.

    NOTE: in order for pagination to work, everything is sorted by '_id'
    -> ids are time-sortable, so there is less possibility of race condition
       in results if the db state changes between user's subsequent calls
    """

    # arg: query -- use 'after'
    if after:
        query["_id"] = {"$gt": ObjectId(after)}

    # arg: projection
    if "_id" in projection:
        projection.remove("_id")

    # search -- when memory gets too high, stop & send last id to user
    last_id = None
    next_after = None
    matches = []
    total_bytes = 0
    async for m in coll.find_all(query, projection, no_id=False, sort=[("_id", 1)]):
        total_bytes += len(
            json.dumps(
                {k: v for k, v in m.items() if k != "_id"}  # '_id' is not JSON-friendly
            ).encode()
        )
        if total_bytes > ENV.USER_QUERY_MAX_BYTES:
            next_after = str(last_id) if last_id else None
            break  # stop right before limit is exceeded
        else:
            last_id = m.pop("_id")
            matches.append(m)

    return matches, next_after
