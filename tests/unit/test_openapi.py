"""Test openapi routes."""

import inspect
import logging
import os
import re
from pathlib import Path

import openapi_core
import tornado
from jsonschema_path import SchemaPath
from openapi_core.templating.paths.finders import APICallPathFinder

from wms import server

LOGGER = logging.getLogger(__name__)

logging.getLogger("parse").setLevel(logging.INFO)


_OPENAPI_SPEC = SchemaPath.from_file_path(
    str(Path(__file__).parent / "../../wms/" / os.environ["REST_OPENAPI_SPEC_FPATH"])
)


def test_census_routes() -> None:
    """Check that all the routes have openapi schemas."""
    missing: list[tuple[str, str]] = []

    for handler in server.HANDLERS:
        route = re.sub(
            r"\(\?P<([^>]+)>\\w\+\)",  # match named groups: (?P<task_id>\w+)
            r"{\1}",  # replace w/ braces: {task_id}
            getattr(handler, "ROUTE"),
        ).rstrip("$")
        LOGGER.info(f"Checking route: {route}")

        implemented_rest_methods = [
            name
            # vars() only gets attrs defined explicitly by child class
            for name, attr in vars(handler).items()
            if inspect.isfunction(attr)
            and name.upper() in tornado.web.RequestHandler.SUPPORTED_METHODS
        ]
        for method in implemented_rest_methods:
            LOGGER.info(f"-> method: {method}")

            try:  # except error so we can see what all is missing w/o multiple test runs
                APICallPathFinder(_OPENAPI_SPEC, base_url=None).find(
                    method,
                    route,
                )
            except openapi_core.templating.paths.exceptions.PathNotFound:
                missing.append((route, method))
                LOGGER.info("----> not found")
            else:
                LOGGER.info("----> found")

    # log at end so these are easy to find
    for missed in missing:
        LOGGER.critical(f"rest route not found in openapi schema: {missed}")
    assert not missing
