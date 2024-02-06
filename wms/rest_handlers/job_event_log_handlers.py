"""REST handlers for condor job event log-related routes."""


import logging

from .. import config
from . import auth, utils
from .base_handlers import BaseWMSHandler

LOGGER = logging.getLogger(__name__)

openapi_validator = utils.OpenAPIValidator(config.REST_OPENAPI_SPEC)


class JobEventLogHandler(BaseWMSHandler):  # pylint: disable=W0223
    """Handle actions with a job event log."""

    ROUTE = r"/tms/job-event-log/(?P<jel_fpath>\w+)$"

    @auth.service_account_auth(roles=[auth.AuthAccounts.TMS])  # type: ignore
    @openapi_validator.validate_request()  # type: ignore[misc, no-untyped-call]
    async def post(self, jel_fpath: str) -> None:
        """Handle POST."""
        self.write({})


# ----------------------------------------------------------------------------
