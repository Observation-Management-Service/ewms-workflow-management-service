"""Test patterns for the server's routes."""


import logging
import re

from wms import server

LOGGER = logging.getLogger(__name__)


def test_route_patterns() -> None:
    """Check that all the routes have non-conflicting patterns.

    Route patterns are matched by the server in the order they were
    added. So, check if "later" patterns would be matched to "earlier"
    patterns.
    """
    routes = [getattr(h, "ROUTE") for h in server.HANDLERS]

    for i, pattern in enumerate(routes):
        for j, this in enumerate(routes):
            if i >= j:  # not yet
                continue
            LOGGER.info(f"applying '{pattern=}' to '{this}'")
            assert not re.match(pattern, this.rstrip("$"))
            LOGGER.info("   -> ok (no match)")
