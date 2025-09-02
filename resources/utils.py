"""Utility functions for the resources python modules."""

import logging
from pathlib import Path

from rest_tools.client import RestClient, SavedDeviceGrantAuth


def get_rest_client(ewms_suffix: str) -> RestClient:
    """Get REST client for talking to EWMS.

    This will present a QR code in the terminal for initial validation.
    """
    ewms_url = f"https://ewms-{ewms_suffix}.icecube.aq"
    logging.info(f"connecting to {ewms_url}...")

    # NOTE: If your script will not be interactive (like a cron job),
    # then you need to first run your script manually to validate using
    # the QR code in the terminal.

    return SavedDeviceGrantAuth(
        ewms_url,
        token_url="https://keycloak.icecube.wisc.edu/auth/realms/IceCube",
        filename=str(
            Path(f"~/device-refresh-token-ewms-{ewms_suffix}").expanduser().resolve()
        ),
        client_id=f"ewms-{ewms_suffix}-public",  # ex: ewms-prod-public
        retries=10,
    )
