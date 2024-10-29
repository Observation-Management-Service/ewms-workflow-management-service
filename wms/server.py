"""Root python script for WMS REST API server interface."""

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
    rest_handlers.workflow_handlers.WorkflowsFindHandler,  # must be before ID handler for regex
    rest_handlers.workflow_handlers.WorkflowIDHandler,  # ^^^
    rest_handlers.workflow_handlers.WorkflowIDActionsAbortHandler,  # ^^^
    rest_handlers.workflow_handlers.WorkflowIDActionsFinishedHandler,  # ^^^
    #
    rest_handlers.task_handlers.TaskDirectivesFindHandler,  # must be before ID handler for regex
    rest_handlers.task_handlers.TaskDirectiveIDHandler,  # ^^^
    #
    rest_handlers.taskforce_handlers.TMSTaskforcesReportHandler,
    rest_handlers.taskforce_handlers.TaskforcesFindHandler,  # must be before ID handler for regex
    rest_handlers.taskforce_handlers.TaskforceUUIDHandler,  # ^^^
    #
    rest_handlers.taskforce_handlers.TMSTaskforcePendingStarterHandler,
    rest_handlers.taskforce_handlers.TMSTaskforceCondorSubmitUUIDHandler,
    rest_handlers.taskforce_handlers.TMSTaskforceCondorSubmitUUIDFailedHandler,
    rest_handlers.taskforce_handlers.TMSTaskforcePendingStopperHandler,
    rest_handlers.taskforce_handlers.TMSTaskforceCondorRmUUIDHandler,
    rest_handlers.taskforce_handlers.TMSTaskforceCondorRmUUIDFailedHandler,
    rest_handlers.taskforce_handlers.TMSTaskforceCondorCompleteUUIDHandler,
]


async def make(mongo_client: AsyncIOMotorClient) -> RestServer:
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

    # Configure REST Routes
    rs = RestServer(debug=ENV.CI)

    for klass in HANDLERS:
        # register route handler
        route = getattr(klass, "ROUTE")  # -> AttributeError
        rs.add_route(route, klass, args)
        LOGGER.info(f"Added handler: {klass.__name__}")

    return rs
