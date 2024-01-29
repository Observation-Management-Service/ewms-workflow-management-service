"""Handlers for the WMS REST API server interface."""


import asyncio
import dataclasses as dc
import json
import logging
import uuid
from typing import Any, Type, TypeVar

import humanfriendly
import kubernetes.client  # type: ignore[import-untyped]
from dacite import from_dict
from dacite.exceptions import DaciteError
from motor.motor_asyncio import AsyncIOMotorClient
from rest_tools.server import RestHandler, token_attribute_role_mapping_auth
from tornado import web

from . import database, images, k8s
from .config import (
    DEFAULT_K8S_CONTAINER_MEMORY_SKYSCAN_SERVER_BYTES,
    DEFAULT_WORKER_DISK_BYTES,
    DEFAULT_WORKER_MEMORY_BYTES,
    ENV,
    KNOWN_CLUSTERS,
    SCAN_MIN_PRIORITY_TO_START_NOW,
    DebugMode,
    is_testing,
)

LOGGER = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# REST requestor auth


USER_ACCT = "user"
TMS_ACCT = "system-tms"


if is_testing():

    def service_account_auth(**kwargs):  # type: ignore
        def make_wrapper(method):  # type: ignore[no-untyped-def]
            async def wrapper(self, *args, **kwargs):  # type: ignore[no-untyped-def]
                LOGGER.warning("TESTING: auth disabled")
                return await method(self, *args, **kwargs)

            return wrapper

        return make_wrapper

else:
    service_account_auth = token_attribute_role_mapping_auth(  # type: ignore[no-untyped-call]
        role_attrs={
            USER_ACCT: ["groups=/institutions/IceCube.*"],
            TMS_ACCT: ["ewms_role=system-tms"],
        }
    )


# -----------------------------------------------------------------------------
# utils


# -----------------------------------------------------------------------------
# handlers


class BaseWMSHandler(RestHandler):  # pylint: disable=W0223
    """BaseWMSHandler is a RestHandler for all WMS routes."""

    def initialize(  # type: ignore  # pylint: disable=W0221
        self,
        mongo_client: AsyncIOMotorClient,  # type: ignore[valid-type]
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize a BaseWMSHandler object."""
        super().initialize(*args, **kwargs)  # type: ignore[no-untyped-call]
        # pylint: disable=W0201
        self.task_directives = database.interface.TaskDirectivesClient(mongo_client)
        self.backlog = database.interface.BacklogClient(mongo_client)


# ----------------------------------------------------------------------------


class MainHandler(BaseWMSHandler):  # pylint: disable=W0223
    """MainHandler is a BaseWMSHandler that handles the root route."""

    ROUTE = r"/$"

    @service_account_auth(roles=[USER_ACCT])  # type: ignore
    async def get(self) -> None:
        """Handle GET."""
        self.write({})


# -----------------------------------------------------------------------------


f"/tms/job-event-log/{urllib.parse.quote(str(jel_fpath),safe='')}",


f"/tms/taskforce/running/{args['taskforce_uuid']}",

f"/tms/taskforce/stop/{args['taskforce_uuid']}",

f"/tms/taskforce/{taskforce_uuid}",

"/tms/taskforces/find"
"/tms/taskforce/pending"
"/tms/taskforces/report"
"/tms/taskforce/stop"
