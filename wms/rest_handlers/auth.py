"""Constants and tools for handling REST-requestor auth."""


import logging

from rest_tools.server import token_attribute_role_mapping_auth

from ..config import is_testing

LOGGER = logging.getLogger(__name__)


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
