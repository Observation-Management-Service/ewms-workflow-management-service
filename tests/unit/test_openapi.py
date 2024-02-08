"""Test openapi routes."""


import inspect
import logging
from pathlib import Path

import openapi_core
import tornado
from openapi_core.templating.paths.finders import APICallPathFinder
from wms import server

LOGGER = logging.getLogger(__name__)


_OPENAPI_JSON = Path(__file__).parent / "../../wms/schema/rest_openapi.json"
_OPENAPI_SPEC = openapi_core.Spec.from_file_path(str(_OPENAPI_JSON))


def test_census_routes() -> None:
    """Check that all the routes have openapi schemas."""
    missing: list[tuple[str, str]] = []

    for handler in server.HANDLERS:
        LOGGER.info(f"Checking route: {handler}")
        implemented_rest_methods = [
            name
            # vars() only gets attrs defined explicitly by child class
            for name, attr in vars(handler).items()
            if inspect.isfunction(attr)
            and name.upper() in tornado.web.RequestHandler.SUPPORTED_METHODS
        ]
        for method in implemented_rest_methods:
            LOGGER.info(f"-> method: {method}")
            route = getattr(handler, "ROUTE")
            try:
                APICallPathFinder(_OPENAPI_SPEC, base_url=None).find(
                    method,
                    route,
                )
            except openapi_core.templating.paths.exceptions.PathNotFound:
                missing.append((route, method))

    assert not missing
