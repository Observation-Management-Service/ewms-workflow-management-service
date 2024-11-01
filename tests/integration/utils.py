"""Test utility functions."""

import json
from typing import Any

import openapi_core
from rest_tools.client import RestClient
from rest_tools.client.utils import request_and_validate

ROUTE_VERSION_PREFIX = "v0"


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


async def check_taskforce_states(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    task_id: str,
    n_taskforces: int,
    phase: str,
    last_phase_change: tuple[str, bool],
) -> None:
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "POST",
        f"/{ROUTE_VERSION_PREFIX}/query/taskforces",
        {
            "query": {"task_id": task_id},
            "projection": ["phase", "phase_change_log"],
        },
    )
    # fmt: off
    assert [tf["phase"] for tf in resp["taskforces"]] == [phase] * n_taskforces
    for tf in resp["taskforces"]:
        assert tf["phase_change_log"][-1]["target_phase"] == last_phase_change[0]
        assert tf["phase_change_log"][-1]["was_successful"] is last_phase_change[1]
    # fmt: on


async def check_workflow_deactivation(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    workflow_id: str,
    kind_of_deactivation: str | None,
) -> None:
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "GET",
        f"/{ROUTE_VERSION_PREFIX}/workflows/{workflow_id}",
    )
    assert resp["deactivated"] == kind_of_deactivation


async def check_nothing_to_start(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    condor_locations: dict[str, Any],
) -> None:
    for loc in condor_locations.values():
        # check that there is NOTHING to start
        assert not await _request_and_validate_and_print(
            rc,
            openapi_spec,
            "GET",
            f"/{ROUTE_VERSION_PREFIX}/tms/pending-starter/taskforces",
            {"collector": loc["collector"], "schedd": loc["schedd"]},
        )


async def check_nothing_to_stop(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    condor_locations: dict[str, Any],
) -> None:
    for loc in condor_locations.values():
        # check that there is NOTHING to stop
        assert not await _request_and_validate_and_print(
            rc,
            openapi_spec,
            "GET",
            f"/{ROUTE_VERSION_PREFIX}/tms/pending-stopper/taskforces",
            {"collector": loc["collector"], "schedd": loc["schedd"]},
        )
