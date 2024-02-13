"""Test patterns for the server's routes."""


import logging
import re

from wms import server

LOGGER = logging.getLogger(__name__)


def test_route_patterns() -> None:
    """Check that all the routes have non-conflicting patterns.

    Route patterns are matched by the server in the order they were
    added. So, check these in that order.
    """
    for pattern in [getattr(h, "ROUTE") for h in server.HANDLERS]:
        LOGGER.info(f"looking at route pattern: '{pattern}'")

        for this in [getattr(h, "ROUTE") for h in server.HANDLERS]:
            if this == pattern:
                break
            LOGGER.info(f"   -> comparing '{pattern}' to '{this}'")
            assert not re.match(pattern, this.rstrip("$"))
            LOGGER.info("   -> ok")
