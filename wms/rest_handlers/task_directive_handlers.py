"""REST handlers for task-related routes."""

import logging
import time

from rest_tools.server import validate_request
from tornado import web

from . import auth
from .base_handlers import BaseWMSHandler
from .. import config
from ..database.client import DocumentNotFoundException
from ..schema.enums import TaskforcePhase
from ..utils import IDFactory

LOGGER = logging.getLogger(__name__)


def _make_taskforce_object(
    workflow_id: str,
    task_id: str,
    cluster_location: str,
    pilot_config: dict,
    worker_config: dict,
    n_workers: int,
    #
    source_entity: str,
    creation_reason: str,
) -> dict:
    """Make a taskforce object from user-supplied data."""
    return {
        # IMMUTABLE
        #
        "taskforce_uuid": IDFactory.generate_taskforce_id(task_id),  # type: ignore
        "task_id": task_id,
        "workflow_id": workflow_id,
        "timestamp": time.time(),
        "collector": config.KNOWN_CLUSTERS[cluster_location]["collector"],
        "schedd": config.KNOWN_CLUSTERS[cluster_location]["schedd"],
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
        #
        # updated by taskforce_launch_control, tms
        # NOTE - for TMS-initiated additional taskforces, this would skip to pre-launch (or pending-starter)
        "phase": TaskforcePhase.PRE_MQ_ACTIVATOR,
        "phase_change_log": [
            {
                "target_phase": TaskforcePhase.PRE_MQ_ACTIVATOR,
                "timestamp": time.time(),
                "source_event_time": None,
                "was_successful": True,
                "source_entity": source_entity,
                "context": creation_reason,
            }
        ],
        #
        # updated by tms SEVERAL times
        "compound_statuses": {},
        "top_task_errors": {},
    }


async def make_task_directive_object_and_taskforce_objects(
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
        "task_id": IDFactory.generate_task_id(workflow_id),
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
            _make_taskforce_object(
                task_directive["workflow_id"],  # type: ignore  # could also use 'workflow_id' var
                task_directive["task_id"],  # type: ignore
                location,
                pilot_config,
                worker_config,
                n_workers,
                "USER",
                "Created during initial workflow request.",
            )
        )

    return task_directive, taskforces


# --------------------------------------------------------------------------------------


class TaskDirectiveIDHandler(BaseWMSHandler):
    """Handle actions for a task's directive."""

    ROUTE = rf"/{config.ROUTE_VERSION_PREFIX}/task-directives/(?P<task_id>[\w-]+)$"

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


# --------------------------------------------------------------------------------------


class TaskDirectivesFindHandler(BaseWMSHandler):
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


# --------------------------------------------------------------------------------------


class TaskDirectiveIDActionsAddWorkersHandler(BaseWMSHandler):
    """Handle actions for creating additional taskforces."""

    ROUTE = rf"/{config.ROUTE_VERSION_PREFIX}/task-directives/(?P<task_id>[\w-]+)/actions/add-workers$"

    @auth.service_account_auth(roles=auth.ALL_AUTH_ACCOUNTS)  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self, task_id: str) -> None:
        """Handle POST.

        Create an additional taskforce.
        """
        async with await self.wms_db.mongo_client.start_session() as s:
            async with s.start_transaction():  # atomic

                # grab fields from an existing taskforce -- copy over common fields
                an_existing_taskforce = (
                    await self.wms_db.taskforces_collection.find_one(
                        {"task_id": task_id},
                        session=s,
                    )
                )

                # first, check that the workflow is not deactivated
                workflow = await self.wms_db.workflows_collection.find_one(
                    {"workflow_id": an_existing_taskforce["workflow_id"]},
                    session=s,
                )
                if workflow["deactivated"] is not None:
                    # adding a taskforce to a deactivated workflow is logically invalid
                    raise web.HTTPError(
                        status_code=422,  # Unprocessable Entity
                        reason=(  # to client
                            f"cannot add a taskforce to a deactivated workflow "
                            f"({an_existing_taskforce["workflow_id"]})"
                        ),
                    )

                # make taskforce & put it into db
                taskforce = _make_taskforce_object(
                    an_existing_taskforce["workflow_id"],
                    an_existing_taskforce["task_id"],  # could also use 'task_id' arg
                    self.get_argument("cluster_location"),
                    an_existing_taskforce["pilot_config"],
                    an_existing_taskforce["worker_config"],
                    self.get_argument("n_workers"),  # TODO: make optional/smart?
                    auth.AuthAccounts(self.auth_roles[0]).name,  # type: ignore
                    "Created when adding more workers for this task directive.",
                )
                taskforce = await self.wms_db.taskforces_collection.insert_one(
                    taskforce,
                    session=s,
                )

        self.write(taskforce)


# --------------------------------------------------------------------------------------
