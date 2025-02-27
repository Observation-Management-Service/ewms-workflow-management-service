"""Utils."""

import asyncio
import logging
import time
import uuid
from functools import wraps

from rest_tools.client import ClientCredentialsAuth, RestClient

from wms.config import ENV


def resilient_daemon_task(restart_delay: float, logger: logging.Logger):
    """A decorator that makes an async function a resilient daemon task."""

    def _decorator(func):
        @wraps(func)
        async def _wrapper(*args, **kwargs):
            while True:
                try:
                    await func(*args, **kwargs)
                except Exception as e:
                    logger.exception("Daemon task encountered an error:", exc_info=e)
                logger.info(f"Restarting daemon task after {restart_delay}s...")
                await asyncio.sleep(restart_delay)

        return _wrapper

    return _decorator


def get_mqs_connection(logger: logging.Logger) -> RestClient:
    """Connect to MQS rest server."""
    if ENV.CI:
        return RestClient(
            ENV.MQS_ADDRESS,
            logger=logger,
        )
    else:
        return ClientCredentialsAuth(
            ENV.MQS_ADDRESS,
            ENV.MQS_TOKEN_URL,
            ENV.MQS_CLIENT_ID,
            ENV.MQS_CLIENT_SECRET,
            logger=logger,
        )


class IDFactory:
    """Factory for creating IDs for the main objects."""

    WORKFLOW_ID_PREFIX = "WF"
    TASK_ID_PREFIX = "TK"
    TASKFORCE_ID_PREFIX = "TF"

    @staticmethod
    def _generate_random_eight_hex() -> str:
        return uuid.uuid4().hex[-8:]

    @staticmethod
    def generate_workflow_id() -> str:
        """Generate an ID for a workflow."""
        hex_time = str(hex(int(time.time()))).removeprefix("0x")
        eight = IDFactory._generate_random_eight_hex()
        return f"{IDFactory.WORKFLOW_ID_PREFIX}-{hex_time}-{eight}"

    @staticmethod
    def generate_task_id(workflow_id: str) -> str:
        """Generate an ID for a task."""
        base = workflow_id.removeprefix(IDFactory.WORKFLOW_ID_PREFIX + "-")
        eight = IDFactory._generate_random_eight_hex()
        return f"{IDFactory.TASK_ID_PREFIX}-{base}-{eight}"

    @staticmethod
    def generate_taskforce_id(task_id: str) -> str:
        """Generate an ID for a taskforce."""
        base = task_id.removeprefix(IDFactory.TASK_ID_PREFIX + "-")
        eight = IDFactory._generate_random_eight_hex()
        return f"{IDFactory.TASKFORCE_ID_PREFIX}-{base}-{eight}"
