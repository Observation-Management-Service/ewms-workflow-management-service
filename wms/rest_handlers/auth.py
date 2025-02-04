"""Constants and tools for handling REST-requestor auth."""

import enum
import logging

from rest_tools.server import token_attribute_role_mapping_auth

from ..config import ENV

LOGGER = logging.getLogger(__name__)


class AuthAccounts(enum.StrEnum):  # attrs are str subclass types! (no `.value` needed)
    """Accounts for auth."""

    USER = "user"
    TMS = "system-tms"


ALL_AUTH_ACCOUNTS = list(AuthAccounts.__members__.values())


if ENV.CI:

    def service_account_auth(roles: list[str], **kwargs):  # type: ignore
        def make_wrapper(method):  # type: ignore[no-untyped-def]
            async def wrapper(self, *args, **kwargs):  # type: ignore[no-untyped-def]
                LOGGER.warning("TESTING: auth disabled")
                self.auth_roles = [roles[0]]  # make as a list containing just 1st role
                return await method(self, *args, **kwargs)

            return wrapper

        return make_wrapper

else:
    service_account_auth = token_attribute_role_mapping_auth(  # type: ignore[no-untyped-call]
        role_attrs={
            AuthAccounts.USER: [
                "groups=/institutions/IceCube.*",
                "groups=/tokens/ewms-dev",
                "ewms_role=user",
            ],
            AuthAccounts.TMS: ["ewms_role=system-tms"],
        }
    )
