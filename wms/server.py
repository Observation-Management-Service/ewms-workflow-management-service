"""Root python script for WMS REST API server interface."""


import logging
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient
from rest_tools.server import RestHandlerSetup, RestServer

from . import rest_handlers
from .config import ENV, is_testing

LOGGER = logging.getLogger(__name__)


async def make(mongo_client: AsyncIOMotorClient) -> RestServer:  # type: ignore[valid-type]
    """Make a WMS REST service (does not start up automatically)."""
    debug = is_testing()

    rhs_config: dict[str, Any] = {"debug": debug}
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
    rs = RestServer(debug=debug)

    for klass in [
        rest_handlers.base_handlers.MainHandler,
        #
        rest_handlers.job_event_log_handlers.JobEventLogHandler,
        #
        rest_handlers.taskforce_handlers.TaskforceHandlerUUID,
        rest_handlers.taskforce_handlers.TaskforcesFindHandler,
        rest_handlers.taskforce_handlers.TaskforcePendingHandler,
        rest_handlers.taskforce_handlers.TaskforceRunningUUIDHandler,
        rest_handlers.taskforce_handlers.TaskforceStopHandler,
        rest_handlers.taskforce_handlers.TaskforceStopUUIDHandler,
        rest_handlers.taskforce_handlers.TaskforcesReportHandler,
    ]:
        # register route handler
        route = getattr(klass, "ROUTE")  # -> AttributeError
        rs.add_route(route, klass, args)
        LOGGER.info(f"Added handler: {klass.__name__}")

        # register a JSON-schema handler (if present)
        try:
            jsh = rest_handlers.schema_handlers.get_json_schema_handler(route)
        except KeyError:
            pass
        else:
            rs.add_route(getattr(jsh, "ROUTE"), jsh, args)  # -> AttributeError
            LOGGER.info(f"Added JSON-schema handler for {klass.__name__}")

    return rs