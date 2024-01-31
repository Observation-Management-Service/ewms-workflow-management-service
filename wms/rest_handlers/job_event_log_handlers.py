"""REST handlers for condor job event log-related routes."""


import logging

from .. import config
from . import auth, utils
from .base_handlers import BaseWMSHandler

LOGGER = logging.getLogger(__name__)


class JobEventLogHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with a job event log."""

    ROUTE = r"/tms/job-event-log/(?P<jel_fpath>\w+)$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.TMS])  # type: ignore
    @utils.validate_with_openapi_spec(config.REST_OPENAPI_SPEC)  # type: ignore[misc]
    async def post(self, jel_fpath: str) -> None:
        """Handle POST."""
        self.write({})


# ----------------------------------------------------------------------------
