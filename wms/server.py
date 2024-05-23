"""Root python script for WMS REST API server interface."""

import asyncio
import logging
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient
from rest_tools.server import RestHandlerSetup, RestServer

from . import rest_handlers
from .config import ENV

LOGGER = logging.getLogger(__name__)

HANDLERS = [
    rest_handlers.base_handlers.MainHandler,
    #
    rest_handlers.schema_handlers.SchemaHandler,
    #
    rest_handlers.workflow_handlers.WorkflowHandler,
    rest_handlers.workflow_handlers.WorkflowIDHandler,
    rest_handlers.workflow_handlers.WorkflowsFindHandler,
    #
    rest_handlers.task_handlers.TaskDirectiveIDHandler,
    rest_handlers.task_handlers.TaskDirectivesFindHandler,
    #
    rest_handlers.taskforce_handlers.TaskforcesReportHandler,
    rest_handlers.taskforce_handlers.TaskforcesFindHandler,
    #
    rest_handlers.taskforce_handlers.TaskforcePendingStarterHandler,
    rest_handlers.taskforce_handlers.TaskforceCondorSubmitUUIDHandler,
    rest_handlers.taskforce_handlers.TaskforcePendingStopperHandler,
    rest_handlers.taskforce_handlers.TaskforcePendingStopperUUIDHandler,
    rest_handlers.taskforce_handlers.TaskforceCondorCompleteUUIDHandler,
    rest_handlers.taskforce_handlers.TaskforceUUIDHandler,
]


async def make(
    mongo_client: AsyncIOMotorClient,
    multiupdate_db_lock: asyncio.Lock,
) -> RestServer:
    """Make a WMS REST service (does not start up automatically)."""
    rhs_config: dict[str, Any] = {"debug": ENV.CI}
    if ENV.AUTH_OPENID_URL:
        rhs_config["auth"] = {
            "audience": ENV.AUTH_AUDIENCE,
            "openid_url": ENV.AUTH_OPENID_URL,
        }
    args = RestHandlerSetup(rhs_config)

    #
    # Setup clients/apis
    args["mongo_client"] = mongo_client
    args["multiupdate_db_lock"] = multiupdate_db_lock

    # Configure REST Routes
    rs = RestServer(debug=ENV.CI)

    for klass in HANDLERS:
        # register route handler
        route = getattr(klass, "ROUTE")  # -> AttributeError
        rs.add_route(route, klass, args)
        LOGGER.info(f"Added handler: {klass.__name__}")

    return rs
