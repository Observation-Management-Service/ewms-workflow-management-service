"""Test utility functions."""

import asyncio
import dataclasses
import json
import os
from typing import Any

import openapi_core
from rest_tools.client import RestClient
from rest_tools.client.utils import request_and_validate

_URL_V_PREFIX = "v1"

CONDOR_LOCATIONS_LOOKUP = {
    "test-alpha": {
        "schedd": "SCHEDD1",
    },
    "test-beta": {
        "schedd": "SCHEDD2",
    },
}


@dataclasses.dataclass
class StateForTMS:
    """Complicated tests are bad, but strange dicts are worse."""

    shortname: str
    schedd: str
    n_taskforces: int
    job_event_log_fpath: str = ""


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


async def sleep_until_background_runners_advance_taskforces(n_taskforces: int) -> None:
    ############################################
    # mq activator & launch control runs...
    #   it's going to be unreliable to try to intercept the middle phase, "pre-launch",
    #   so just wait till both run
    ############################################
    await asyncio.sleep(int(os.environ["WORKFLOW_MQ_ACTIVATOR_DELAY"]) * 2)  # pad
    await asyncio.sleep(
        int(os.environ["TASKFORCE_LAUNCH_CONTROL_DELAY"]) * n_taskforces
    )


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
        f"/{_URL_V_PREFIX}/query/taskforces",
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
        f"/{_URL_V_PREFIX}/workflows/{workflow_id}",
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
            f"/{_URL_V_PREFIX}/tms/pending-starter/taskforces",
            {"schedd": loc["schedd"]},
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
            f"/{_URL_V_PREFIX}/tms/pending-stopper/taskforces",
            {"schedd": loc["schedd"]},
        )
