"""Test utility functions."""

import json
from typing import Any

import openapi_core
from rest_tools.client import RestClient
from rest_tools.client.utils import request_and_validate


async def _request_and_validate_and_print(
    rc: RestClient,
    openapi_spec: "openapi_core.OpenAPI",
    method: str,
    path: str,
    args: dict[str, Any] | None = None,
) -> Any:
    print(f"{method} @ {path}:")
    ret = await request_and_validate(rc, openapi_spec, method, path, args)
    print(json.dumps(ret, indent=4))
    return ret
