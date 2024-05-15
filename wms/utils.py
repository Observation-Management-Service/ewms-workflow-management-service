"""Utils."""

import logging

from rest_tools.client import RestClient, ClientCredentialsAuth

from wms.config import ENV


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
