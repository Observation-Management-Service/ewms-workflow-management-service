"""REST handlers for task-related routes."""


import logging
import uuid

from .. import config
from . import auth, utils
from .base_handlers import BaseWMSHandler

LOGGER = logging.getLogger(__name__)


# ----------------------------------------------------------------------------


class TaskDirectiveHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for adding a task directive (initiating a task)."""

    ROUTE = r"/task/directive$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @utils.validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self) -> None:
        """Handle POST."""
        task_directive = dict(
            task_id=uuid.uuid4().hex,
            cluster_locations=[],
            task_image=self.get_argument("task_image"),
            task_args=self.get_argument("task_args", ""),
        )

        task_directive = await self.task_directive_db.insert(task_directive)

        self.write(task_directive)


# ----------------------------------------------------------------------------


class TaskDirectiveIDHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for a task's directive."""

    ROUTE = r"/task/directive/(?P<task_id>\w+)$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @utils.validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def get(self, task_id: str) -> None:
        """Handle GET."""
        self.write(
            {
                "task_image": "icecube/earthpilot",
                "task_args": "aaa bbb --ccc 123",
                "task_id": task_id,
            }
        )


# ----------------------------------------------------------------------------


class TaskDirectivesFindHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions for finding task directives."""

    ROUTE = r"/task/directives/find$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.USER])  # type: ignore
    @utils.validate_request(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self) -> None:
        """Handle POST."""
        self.write(
            {
                "task_directives": [
                    {
                        "task_image": "icecube/earthpilot",
                        "task_args": "aaa bbb --ccc 123",
                        "task_id": "abcdef123456",
                    },
                ]
            }
        )


# ----------------------------------------------------------------------------
