"""Common high-level actions that occur in many situations."""

import asyncio
import copy
import json
import logging
import os
import time
from pathlib import Path

import openapi_core
from jsonschema_path import SchemaPath
from rest_tools.client import RestClient
from rest_tools.client.utils import request_and_validate

from utils import _request_and_validate_and_print

LOGGER = logging.getLogger(__name__)


_OPENAPI_JSON = (
    Path(__file__).parent / "../../wms/" / os.environ["REST_OPENAPI_SPEC_FPATH"]
)
ROUTE_VERSION_PREFIX = "v0"


async def query_for_schema(rc: RestClient) -> openapi_core.OpenAPI:
    """Get the OpenAPI schema."""
    resp = await request_and_validate(
        rc,
        # only read json file for this request
        openapi_core.OpenAPI(SchemaPath.from_file_path(str(_OPENAPI_JSON))),
        "GET",
        f"/{ROUTE_VERSION_PREFIX}/schema/openapi",
    )
    with open(_OPENAPI_JSON, "rb") as f:
        assert json.load(f) == resp
    openapi_spec = openapi_core.OpenAPI(SchemaPath.from_dict(resp))

    return openapi_spec


async def user_requests_new_workflow(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    condor_locations: dict,
) -> tuple[str, str]:
    """Return workflow and task ids."""
    task_image = "icecube/earthpilot"
    task_args = "aaa bbb --ccc 123"
    n_workers = 99
    worker_config = {
        "do_transfer_worker_stdouterr": False,
        "max_worker_runtime": 60 * 60 * 1,
        "n_cores": 4,
        "priority": 1,
        "worker_disk": "1G",
        "worker_memory": "512M",
    }
    environment: dict[str, str] = {}
    input_files: list[str] = []

    #
    # USER...
    # requests new workflow
    #
    workflow_resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "POST",
        f"/{ROUTE_VERSION_PREFIX}/workflows",
        {
            "tasks": [
                {
                    "cluster_locations": list(condor_locations.keys()),
                    "task_image": task_image,
                    "task_args": task_args,
                    "input_queue_aliases": ["qfoo"],
                    "output_queue_aliases": ["qbar"],
                    #
                    "n_workers": n_workers,
                    "worker_config": worker_config,
                    # environment=environment,  # empty
                    # input_files=input_files,  # empty
                }
            ],
            "public_queue_aliases": ["qfoo", "qbar"],
        },
    )
    # TODO - update asserts when/if testing multi-task workflows
    assert workflow_resp["workflow"]
    assert len(workflow_resp["task_directives"]) == 1
    assert len(workflow_resp["taskforces"]) == 2
    # taskforce checks
    assert all(tf["phase"] == "pre-mq-activation" for tf in workflow_resp["taskforces"])
    assert all(
        tf["phase_change_log"][-1]["target_phase"] == "pre-mq-activation"
        for tf in workflow_resp["taskforces"]
    )
    assert len(workflow_resp["taskforces"]) == len(condor_locations)
    assert sorted(  # check locations were translated correctly to collector+schedd
        (tf["collector"], tf["schedd"]) for tf in workflow_resp["taskforces"]
    ) == sorted((loc["collector"], loc["schedd"]) for loc in condor_locations.values())
    assert all(
        tf["worker_config"] == worker_config for tf in workflow_resp["taskforces"]
    )
    assert all(tf["n_workers"] == n_workers for tf in workflow_resp["taskforces"])
    for tf in workflow_resp["taskforces"]:
        expected = {
            "tag": os.environ["TEST_PILOT_IMAGE_LATEST_TAG"],
            "environment": {
                **environment,
                "EWMS_PILOT_TASK_IMAGE": task_image,
                "EWMS_PILOT_TASK_ARGS": task_args,
            },
            "input_files": input_files,
        }
        print(tf["pilot_config"])
        print(expected)
        assert tf["pilot_config"] == expected

    ############################################
    # mq activator & launch control runs...
    #   it's going to be unreliable to try to intercept the middle phase, "pre-launch",
    #   so just wait till both run
    ############################################
    await asyncio.sleep(int(os.environ["WORKFLOW_MQ_ACTIVATOR_DELAY"]) * 2)  # pad
    await asyncio.sleep(
        int(os.environ["TASKFORCE_LAUNCH_CONTROL_DELAY"])
        * len(workflow_resp["taskforces"])
    )

    # query about task directive
    task_directive = workflow_resp["task_directives"][0]
    task_id = task_directive["task_id"]
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "GET",
        f"/{ROUTE_VERSION_PREFIX}/task-directives/{task_id}",
    )
    assert resp == task_directive
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "POST",
        f"/{ROUTE_VERSION_PREFIX}/query/task-directives",
        {"query": {"task_id": task_id}},
    )
    assert len(resp["task_directives"]) == 1
    assert resp["task_directives"][0] == task_directive

    # look at taskforces
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "POST",
        f"/{ROUTE_VERSION_PREFIX}/query/taskforces",
        {
            "query": {"task_id": task_id},
        },
    )
    assert all(tf["phase"] == "pending-starter" for tf in resp["taskforces"])
    assert all(
        tf["phase_change_log"][-1]["target_phase"] == "pending-starter"
        for tf in resp["taskforces"]
    )
    assert all(
        tf["pilot_config"]["environment"]
        == {
            **environment,
            #
            "EWMS_PILOT_TASK_IMAGE": task_image,
            "EWMS_PILOT_TASK_ARGS": task_args,
            #
            "EWMS_PILOT_QUEUE_INCOMING": ["123qfoo"],
            "EWMS_PILOT_QUEUE_INCOMING_AUTH_TOKEN": ["DUMMY_TOKEN"],
            "EWMS_PILOT_QUEUE_INCOMING_BROKER_ADDRESS": ["DUMMY_BROKER_ADDRESS"],
            "EWMS_PILOT_QUEUE_INCOMING_BROKER_TYPE": ["DUMMY_BROKER_TYPE"],
            #
            "EWMS_PILOT_QUEUE_OUTGOING": ["123qbar"],
            "EWMS_PILOT_QUEUE_OUTGOING_AUTH_TOKEN": ["DUMMY_TOKEN"],
            "EWMS_PILOT_QUEUE_OUTGOING_BROKER_ADDRESS": ["DUMMY_BROKER_ADDRESS"],
            "EWMS_PILOT_QUEUE_OUTGOING_BROKER_TYPE": ["DUMMY_BROKER_TYPE"],
        }
        for tf in resp["taskforces"]
    )

    return workflow_resp["workflow"]["workflow_id"], task_id


async def tms_starter(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    task_id: str,
    condor_locations: dict,
) -> dict:
    condor_locs_w_jel = copy.deepcopy(condor_locations)

    #
    # TMS(es) starter(s)...
    #
    for shortname, loc in condor_locations.items():
        # get next to start
        taskforce = await _request_and_validate_and_print(
            rc,
            openapi_spec,
            "GET",
            f"/{ROUTE_VERSION_PREFIX}/tms/pending-starter/taskforces",
            {"collector": loc["collector"], "schedd": loc["schedd"]},
        )
        assert taskforce
        taskforce_uuid = taskforce["taskforce_uuid"]
        # check that it's still pending
        resp = await _request_and_validate_and_print(
            rc,
            openapi_spec,
            "GET",
            f"/{ROUTE_VERSION_PREFIX}/taskforces/{taskforce_uuid}",
        )
        assert resp["phase"] == "pending-starter"
        # confirm it has started
        condor_locs_w_jel[shortname]["jel"] = "/home/the_job_event_log_fpath"
        resp = await _request_and_validate_and_print(
            rc,
            openapi_spec,
            "POST",
            f"/{ROUTE_VERSION_PREFIX}/tms/condor-submit/taskforces/{taskforce_uuid}",
            {
                "cluster_id": 123456,
                "n_workers": 5600,
                "submit_dict": {"foo": 123, "bar": "abc"},
                "job_event_log_fpath": condor_locs_w_jel[shortname]["jel"],
            },
        )

    #
    # USER...
    # check above
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "POST",
        f"/{ROUTE_VERSION_PREFIX}/query/taskforces",
        {
            "query": {
                "task_id": task_id,
            },
            "projection": ["phase", "phase_change_log"],
        },
    )
    assert len(resp["taskforces"]) == len(condor_locations)
    assert all(tf["phase"] == "condor-submit" for tf in resp["taskforces"])
    assert all(
        tf["phase_change_log"][-1]["target_phase"] == "condor-submit"
        for tf in resp["taskforces"]
    )
    # check directive reflects startup (runtime-assembled list of taskforces)
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "POST",
        f"/{ROUTE_VERSION_PREFIX}/query/taskforces",
        {
            "query": {"task_id": task_id},
            "projection": ["collector", "schedd"],
        },
    )
    assert len(resp["taskforces"]) == len(condor_locations)
    for loc in condor_locations.values():
        assert {"collector": loc["collector"], "schedd": loc["schedd"]} in resp[
            "taskforces"
        ]

    return condor_locs_w_jel


async def tms_watcher_sends_status_update(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    task_id: str,
    condor_locs_w_jel: dict,
    top_task_errors_by_locshortname: dict,
    compound_statuses_by_locshortname: dict,
) -> None:
    #
    # TMS(es) watcher(s)...
    # jobs in action!
    #
    for shortname, loc in condor_locs_w_jel.items():
        resp = await _request_and_validate_and_print(
            rc,
            openapi_spec,
            "POST",
            f"/{ROUTE_VERSION_PREFIX}/query/taskforces",
            {
                "query": {
                    "collector": loc["collector"],
                    "schedd": loc["schedd"],
                    "job_event_log_fpath": loc["jel"],
                },
                "projection": ["taskforce_uuid", "cluster_id"],
            },
        )
        assert len(resp["taskforces"]) == 1
        taskforce_uuid = resp["taskforces"][0]["taskforce_uuid"]
        resp = await _request_and_validate_and_print(
            rc,
            openapi_spec,
            "POST",
            f"/{ROUTE_VERSION_PREFIX}/tms/statuses/taskforces",
            {
                "top_task_errors_by_taskforce": {
                    taskforce_uuid: top_task_errors_by_locshortname[shortname],
                },
                "compound_statuses_by_taskforce": {
                    taskforce_uuid: compound_statuses_by_locshortname[shortname]
                },
            },
        )
        assert resp["results"] == [{"uuid": taskforce_uuid, "status": "updated"}]

    #
    # USER...
    # check above
    #
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "POST",
        f"/{ROUTE_VERSION_PREFIX}/query/taskforces",
        {
            "query": {"task_id": task_id},
            "projection": [
                "taskforce_uuid",
                "compound_statuses",
                "top_task_errors",
                "collector",
                "schedd",
            ],
        },
    )
    assert len(resp["taskforces"]) == len(condor_locs_w_jel)
    for tf in resp["taskforces"]:
        for shortname, loc in condor_locs_w_jel.items():
            if loc["collector"] == tf["collector"] and loc["schedd"] == tf["schedd"]:
                break
        else:
            assert 0  # -> did not find it
        # fmt: off
        # has new vals
        assert tf["compound_statuses"] == compound_statuses_by_locshortname[shortname]
        assert tf["top_task_errors"] == top_task_errors_by_locshortname[shortname]
        # fmt: on


async def user_deactivates_workflow(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    kind_of_deactivation: str,
    task_id: str,
    condor_locations: dict,
    deactivated_after_condor_stopped: bool = False,
) -> None:
    #
    # USER...
    # stop workflow
    #
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "POST",
        f"/{ROUTE_VERSION_PREFIX}/query/task-directives",
        {
            "query": {"task_id": task_id},
            "projection": ["workflow_id"],
        },
    )
    assert len(resp["task_directives"]) == 1
    workflow_id = resp["task_directives"][0]["workflow_id"]
    then = time.time()
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "POST",
        (
            {
                "ABORT": f"/{ROUTE_VERSION_PREFIX}/workflows/{workflow_id}/actions/abort",
                "FINISHED": f"/{ROUTE_VERSION_PREFIX}/workflows/{workflow_id}/actions/finished",
            }[kind_of_deactivation]
        ),
    )
    assert resp == {
        "workflow_id": workflow_id,
        "n_taskforces": (
            len(condor_locations) if not deactivated_after_condor_stopped else 0
        ),
    }
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "GET",
        f"/{ROUTE_VERSION_PREFIX}/workflows/{workflow_id}",
    )
    assert resp["deactivated"] == kind_of_deactivation
    assert then < resp["deactivated_ts"] < time.time()

    if deactivated_after_condor_stopped:
        return

    #
    # USER...
    # check above
    #
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "POST",
        f"/{ROUTE_VERSION_PREFIX}/query/taskforces",
        {
            "query": {
                "task_id": task_id,
            },
            "projection": ["phase", "phase_change_log"],
        },
    )
    assert len(resp["taskforces"]) == len(condor_locations)
    assert all(tf["phase"] == "pending-stopper" for tf in resp["taskforces"])
    assert all(
        tf["phase_change_log"][-1]["target_phase"] == "pending-stopper"
        for tf in resp["taskforces"]
    )


async def tms_stopper(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    task_id: str,
    condor_locations: dict,
) -> None:
    #
    # TMS(es) stopper(s)...
    # this happens even if task aborted before condor
    #
    for loc in condor_locations.values():
        # get next to stop
        taskforce = await _request_and_validate_and_print(
            rc,
            openapi_spec,
            "GET",
            f"/{ROUTE_VERSION_PREFIX}/tms/pending-stopper/taskforces",
            {"collector": loc["collector"], "schedd": loc["schedd"]},
        )
        assert taskforce
        # confirm it has stopped
        resp = await _request_and_validate_and_print(
            rc,
            openapi_spec,
            "POST",
            f"/{ROUTE_VERSION_PREFIX}/tms/condor-rm/taskforces/{taskforce['taskforce_uuid']}",
        )

    #
    # USER...
    # check above
    #
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "POST",
        f"/{ROUTE_VERSION_PREFIX}/query/taskforces",
        {
            "query": {
                "task_id": task_id,
            },
            "projection": ["phase", "phase_change_log"],
        },
    )
    assert len(resp["taskforces"]) == len(condor_locations)
    assert all(tf["phase"] == "condor-rm" for tf in resp["taskforces"])
    assert all(
        tf["phase_change_log"][-1]["target_phase"] == "condor-rm"
        for tf in resp["taskforces"]
    )


async def tms_condor_clusters_done(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    task_id: str,
    condor_locs_w_jel: dict,
) -> None:
    #
    # TMS(es) watcher(s)...
    # taskforces' condor clusters are done
    #
    for loc in condor_locs_w_jel.values():
        resp = await _request_and_validate_and_print(
            rc,
            openapi_spec,
            "POST",
            f"/{ROUTE_VERSION_PREFIX}/query/taskforces",
            {
                "query": {
                    "collector": loc["collector"],
                    "schedd": loc["schedd"],
                    "job_event_log_fpath": loc["jel"],
                },
                "projection": ["taskforce_uuid"],
            },
        )
        assert len(resp["taskforces"]) == 1
        resp = await _request_and_validate_and_print(
            rc,
            openapi_spec,
            "POST",
            f"/{ROUTE_VERSION_PREFIX}/tms/condor-complete/taskforces/{resp['taskforces'][0]['taskforce_uuid']}",
            {
                "condor_complete_ts": (
                    # NOTE: need a unique timestamp that we don't need to rely on the timing of this test
                    hash(resp["taskforces"][0]["taskforce_uuid"])
                    % 1700000000
                ),
            },
        )

    #
    # USER...
    # check above
    #
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "POST",
        f"/{ROUTE_VERSION_PREFIX}/query/taskforces",
        {
            "query": {
                "task_id": task_id,
            },
            "projection": ["taskforce_uuid", "phase_change_log"],
        },
    )
    assert len(resp["taskforces"]) == len(condor_locs_w_jel)
    assert all(
        list(
            pcl["source_event_time"]
            for pcl in tf["phase_change_log"]
            if pcl["target_phase"] == "condor-complete"
        )  # this will also check if there is only 1 matching entry
        == [hash(tf["taskforce_uuid"]) % 1700000000]  # see above
        for tf in resp["taskforces"]
    )
