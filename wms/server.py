"""Root python script for WMS REST API server interface."""


import logging
from typing import Any

import kubernetes.client  # type: ignore[import-untyped]
from motor.motor_asyncio import AsyncIOMotorClient
from rest_tools.server import RestHandlerSetup, RestServer

from . import rest_handlers
from .config import ENV, is_testing

LOGGER = logging.getLogger(__name__)


async def make(
    mongo_client: AsyncIOMotorClient,  # type: ignore[valid-type]
    k8s_batch_api: kubernetes.client.BatchV1Api,
) -> RestServer:
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
    args["k8s_batch_api"] = k8s_batch_api

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
        try:
            rs.add_route(getattr(klass, "ROUTE"), klass, args)
            LOGGER.info(f"Added handler: {klass.__name__}")
        except AttributeError:
            continue

    return rs
