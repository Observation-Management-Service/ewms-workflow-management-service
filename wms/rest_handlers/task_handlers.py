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


async def create_task_directive(
    task_directives_client,
    taskforces_client,
    cluster_locations,
    task_image,
    task_args,
    worker_config,
    n_workers,
    environment,
    input_files,
) -> dict:
    """Create a new task directive."""
    task_directive = dict(
        task_id=uuid.uuid4().hex,
        cluster_locations=cluster_locations,
        task_image=task_image,
        task_args=task_args,
        timestamp=int(time.time()),
        priority=worker_config["priority"],
        #
        n_queues=2,  # TODO: make user configurable?
        queues=[],  # values determined by mqs, updated by task_mq_assembly
        _mqs_retry_at_ts=config.MQS_RETRY_AT_TS_DEFAULT_VALUE,  # updated by task_mq_assembly
        #
        aborted=False,
    )

    # first, check that locations are legit
    for location in task_directive["cluster_locations"]:
        if location not in config.KNOWN_CLUSTERS:
            raise web.HTTPError(
                status_code=400,
                reason=f"condor location not found: {location}",  # to client
            )

    # next, insert
    task_directive = await task_directives_client.insert_one(task_directive)

    # now, create Taskforce entries (important to do now so removals are handled easily--think dangling pointers)
    for location in task_directive["cluster_locations"]:
        await taskforces_client.insert_one(
            dict(
                # STATIC
                taskforce_uuid=uuid.uuid4().hex,
                task_id=task_directive["task_id"],
                timestamp=int(time.time()),
                collector=config.KNOWN_CLUSTERS[location]["collector"],
                schedd=config.KNOWN_CLUSTERS[location]["schedd"],
                #
                # TODO: make optional/smart
                n_workers=n_workers,
                #
                container_config=dict(
                    image=task_directive["task_image"],
                    arguments=task_directive["task_args"],
                    environment=environment,
                    input_files=input_files,
                ),
                worker_config=worker_config,
                #
                # set ONCE by tms via /taskforce/tms-action/condor-submit/<id>
                cluster_id=None,
                submit_dict={},
                job_event_log_fpath="",
                # set ONCE by tms's watcher
                condor_complete_ts=None,
                #
                # updated by taskforce_launch_control, tms
                # NOTE - for TMS-initiated additional taskforces, this would skip to pre-launch (or pending-starter)
                phase=TaskforcePhase.PRE_MQ_ASSEMBLY,
                #
                # updated by tms SEVERAL times
                compound_statuses={},
                top_task_errors={},
            )
        )

    return task_directive


# ----------------------------------------------------------------------------


class TaskDirectiveIDHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for a task's directive."""

    ROUTE = r"/task/directive/(?P<task_id>\w+)$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def get(self, task_id: str) -> None:
        """Handle GET.

        Get an existing task directive.
        """
        try:
            task_directive = await self.task_directives_client.find_one(
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

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def delete(self, task_id: str) -> None:
        """Handle DELETE.

        Abort a task.
        """
        try:
            await self.task_directives_client.find_one_and_update(
                {
                    "task_id": task_id,
                    "aborted": {"$nin": [True]},  # "not in"
                },
                {
                    "aborted": True,
                },
            )
        except DocumentNotFoundException as e:
            raise web.HTTPError(
                status_code=404,
                reason=f"no non-aborted task found with id: {task_id}",  # to client
            ) from e

        # set all corresponding taskforces to pending-stopper
        n_updated = 0  # in case of exception
        try:
            n_updated = await self.taskforces_client.update_set_many(
                {
                    "task_id": task_id,
                    "$and": [
                        # not already aborted
                        # NOTE - we don't care whether the taskforce has started up (see /taskforce/tms-action/pending-stopper)
                        {
                            "phase": {
                                "$nin": [
                                    TaskforcePhase.PENDING_STOPPER,
                                    TaskforcePhase.CONDOR_RM,
                                ]
                            },  # "not in"
                        },
                        # AND
                        # not condor-completed
                        {
                            "condor_complete_ts": None,  # int -> condor-completed
                        },
                    ],
                },
                {
                    "phase": TaskforcePhase.PENDING_STOPPER,
                },
            )
        except DocumentNotFoundException:
            LOGGER.info(
                "okay scenario: task aborted but no taskforces needed to be stopped"
            )

        self.write({"task_id": task_id, "n_taskforces": n_updated})


# ----------------------------------------------------------------------------


class TaskDirectivesFindHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for finding task directives."""

    ROUTE = r"/task/directives/find$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self) -> None:
        """Handle POST.

        Search for task directives matching given query.
        """
        matches = []
        async for m in self.task_directives_client.find_all(
            self.get_argument("query"),
            self.get_argument("projection", []),
        ):
            matches.append(m)

        self.write({"task_directives": matches})


# ----------------------------------------------------------------------------
