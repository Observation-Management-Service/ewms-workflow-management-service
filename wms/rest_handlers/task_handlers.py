"""REST handlers for task-related routes."""

import logging
import time
import uuid

from rest_tools.server import validate_request
from tornado import web

from . import auth
from .base_handlers import BaseWMSHandler
from .. import config
from ..database.client import DocumentNotFoundException
from ..schema.enums import TaskforcePhase

LOGGER = logging.getLogger(__name__)


# ----------------------------------------------------------------------------


async def create_task_directive_and_taskforces(
    workflow_id: str,
    #
    cluster_locations: list[str],
    task_image: str,
    task_args: list[str],
    #
    input_queues: list[str],
    output_queues: list[str],
    #
    pilot_config: dict,
    worker_config: dict,
    n_workers: int,
) -> tuple[dict, list[dict]]:
    """Create new task directive and taskforces."""

    task_directive = {
        # IMMUTABLE
        #
        "task_id": uuid.uuid4().hex,
        "workflow_id": workflow_id,
        "timestamp": time.time(),
        #
        "cluster_locations": cluster_locations,
        "task_image": task_image,
        "task_args": task_args,
        #
        "input_queues": input_queues,
        "output_queues": output_queues,
        #
        # MUTABLE
    }
    pilot_config["environment"].update(
        {
            "EWMS_PILOT_TASK_IMAGE": task_image,
            "EWMS_PILOT_TASK_ARGUMENTS": task_args,
        }
    )

    # first, check that locations are legit
    for location in cluster_locations:
        if location not in config.KNOWN_CLUSTERS:
            raise web.HTTPError(
                status_code=400,
                reason=f"condor location not found: {location}",  # to client
            )

    # now, create Taskforce entries (important to do now so removals are handled easily--think dangling pointers)
    taskforces = []
    for location in cluster_locations:
        taskforces.append(
            {
                # IMMUTABLE
                #
                "taskforce_uuid": uuid.uuid4().hex,
                "task_id": task_directive["task_id"],
                "workflow_id": workflow_id,
                "timestamp": time.time(),
                "collector": config.KNOWN_CLUSTERS[location]["collector"],
                "schedd": config.KNOWN_CLUSTERS[location]["schedd"],
                #
                # TODO: make optional/smart
                "n_workers": n_workers,
                #
                "worker_config": worker_config,
                #
                # MUTABLE
                #
                # 'pilot_config.environment' is appended to by workflow_mq_activator
                "pilot_config": pilot_config,
                #
                # set ONCE by tms via /tms/condor-submit/taskforces/<id>
                "cluster_id": None,
                "submit_dict": {},
                "job_event_log_fpath": "",
                # set ONCE by tms's watcher
                "condor_complete_ts": None,
                #
                # updated by taskforce_launch_control, tms
                # NOTE - for TMS-initiated additional taskforces, this would skip to pre-launch (or pending-starter)
                "phase": TaskforcePhase.PRE_MQ_ACTIVATOR,
                #
                # updated by tms SEVERAL times
                "compound_statuses": {},
                "top_task_errors": {},
            }
        )

    return task_directive, taskforces


# ----------------------------------------------------------------------------


class TaskDirectiveIDHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for a task's directive."""

    ROUTE = rf"/{config.ROUTE_VERSION_PREFIX}/task-directives/(?P<task_id>\w+)$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def get(self, task_id: str) -> None:
        """Handle GET.

        Get an existing task directive.
        """
        try:
            task_directive = await self.wms_db.task_directives_collection.find_one(
                {
                    "task_id": task_id,
                }
            )
        except DocumentNotFoundException as e:
            raise web.HTTPError(
                status_code=404,
                reason=f"no task found with id: {task_id}",  # to client
            ) from e

        self.write(task_directive)


# ----------------------------------------------------------------------------


class TaskDirectivesFindHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for finding task directives."""

    ROUTE = rf"/{config.ROUTE_VERSION_PREFIX}/query/task-directives$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self) -> None:
        """Handle POST.

        Search for task directives matching given query.
        """
        matches = []
        async for m in self.wms_db.task_directives_collection.find_all(
            self.get_argument("query"),
            self.get_argument("projection", []),
        ):
            matches.append(m)

        self.write({"task_directives": matches})


# ----------------------------------------------------------------------------
