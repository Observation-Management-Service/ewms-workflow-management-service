"""Common high-level actions that occur in many situations."""


import copy
import json
import logging
import os
from pathlib import Path

import openapi_core
from jsonschema_path import SchemaPath
from rest_tools.client import RestClient

from utils import request_and_validate

LOGGER = logging.getLogger(__name__)


_OPENAPI_JSON = (
    Path(__file__).parent / "../../wms/" / os.environ["REST_OPENAPI_SPEC_FPATH"]
)


def query_for_schema(rc: RestClient) -> openapi_core.OpenAPI:
    resp = request_and_validate(
        rc,
        # only read json file for this request
        openapi_core.OpenAPI(SchemaPath.from_file_path(str(_OPENAPI_JSON))),
        "GET",
        "/schema/openapi",
    )
    with open(_OPENAPI_JSON, "rb") as f:
        assert json.load(f) == resp
    openapi_spec = openapi_core.OpenAPI(SchemaPath.from_dict(resp))

    return openapi_spec


def user_requests_new_task(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    condor_lnames: list[str],
) -> str:
    #
    # USER...
    # requests new task
    #
    task_directive = request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/task/directive",
        {
            "task_image": "icecube/earthpilot",
            "task_args": "aaa bbb --ccc 123",
            "cluster_locations": condor_lnames,
        },
    )
    task_id = task_directive["task_id"]
    resp = request_and_validate(
        rc,
        openapi_spec,
        "GET",
        f"/task/directive/{task_id}",
    )
    assert resp == task_directive
    resp = request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/task/directives/find",
        {
            "query": {
                "task_image": "icecube/earthpilot",
                "task_args": "aaa bbb --ccc 123",
            }
        },
    )
    assert len(resp["task_directives"]) == 1
    assert resp["task_directives"][0] == task_directive
    resp = request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/tms/taskforces/find",
        {
            "query": {
                "task_id": task_id,
            },
            "projection": ["tms_status"],
        },
    )
    assert len(resp["taskforces"]) == len(condor_lnames)
    assert all(tf["tms_status"] == "pending-start" for tf in resp["taskforces"])

    return task_id  # type: ignore[no-any-return]


def tms_starter(
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
        taskforce = request_and_validate(
            rc,
            openapi_spec,
            "GET",
            "/tms/taskforce/pending",
            {"collector": loc["collector"], "schedd": loc["schedd"]},
        )
        assert taskforce
        taskforce_uuid = taskforce["taskforce_uuid"]
        # check that it's still pending
        resp = request_and_validate(
            rc,
            openapi_spec,
            "GET",
            f"/tms/taskforce/{taskforce_uuid}",
        )
        assert resp["tms_status"] == "pending-start"
        # confirm it has started
        condor_locs_w_jel[shortname]["jel"] = "/home/the_job_event_log_fpath"
        resp = request_and_validate(
            rc,
            openapi_spec,
            "POST",
            f"/tms/taskforce/running/{taskforce_uuid}",
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
    resp = request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/tms/taskforces/find",
        {
            "query": {
                "task_id": task_id,
            },
            "projection": ["tms_status"],
        },
    )
    assert len(resp["taskforces"]) == len(condor_locations)
    assert all(tf["tms_status"] == "running" for tf in resp["taskforces"])
    # check directive reflects startup (runtime-assembled list of taskforces)
    resp = request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/tms/taskforces/find",
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


def tms_watcher_sends_report_update(
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
        resp = request_and_validate(
            rc,
            openapi_spec,
            "POST",
            "/tms/taskforces/find",
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
        resp = request_and_validate(
            rc,
            openapi_spec,
            "POST",
            "/tms/taskforces/report",
            {
                "top_task_errors_by_taskforce": {
                    taskforce_uuid: top_task_errors_by_locshortname[shortname],
                },
                "compound_statuses_by_taskforce": {
                    taskforce_uuid: compound_statuses_by_locshortname[shortname]
                },
            },
        )
        assert resp["taskforce_uuids"] == [taskforce_uuid]

    #
    # USER...
    # check above
    #
    resp = request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/tms/taskforces/find",
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
    print(json.dumps(resp, indent=4))
    assert len(resp["taskforces"]) == len(condor_locs_w_jel)
    for tf in resp["taskforces"]:
        print(tf["taskforce_uuid"])
        for shortname, loc in condor_locs_w_jel.items():
            if loc["collector"] == tf["collector"] and loc["schedd"] == tf["schedd"]:
                break
        assert shortname  # if issue -> did not find it
        print(shortname)
        print(tf["compound_statuses"])
        print(compound_statuses_by_locshortname)
        assert tf["compound_statuses"] == compound_statuses_by_locshortname[shortname]
        print(shortname)
        print(tf["top_task_errors"])
        print(top_task_errors_by_locshortname)
        assert tf["top_task_errors"] == top_task_errors_by_locshortname[shortname]


def user_aborts_task(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    task_id: str,
    condor_locs_w_jel: dict,
) -> None:
    #
    # USER...
    # stop task
    #
    resp = request_and_validate(
        rc,
        openapi_spec,
        "DELETE",
        f"/task/directive/{task_id}",
    )
    assert resp == {"task_id": task_id, "n_taskforces": len(condor_locs_w_jel)}
    resp = request_and_validate(
        rc,
        openapi_spec,
        "GET",
        f"/task/directive/{task_id}",
    )
    assert resp["aborted"] is True
    resp = request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/tms/taskforces/find",
        {
            "query": {
                "task_id": task_id,
            },
            "projection": ["tms_status"],
        },
    )
    assert len(resp["taskforces"]) == len(condor_locs_w_jel)
    assert all(tf["tms_status"] == "pending-stop" for tf in resp["taskforces"])

    #
    # TMS(es) stopper(s)...
    #
    for loc in condor_locs_w_jel.values():
        # get next to stop
        taskforce = request_and_validate(
            rc,
            openapi_spec,
            "GET",
            "/tms/taskforce/stop",
            {"collector": loc["collector"], "schedd": loc["schedd"]},
        )
        assert taskforce
        # confirm it has stopped
        resp = request_and_validate(
            rc,
            openapi_spec,
            "DELETE",
            f"/tms/taskforce/stop/{taskforce['taskforce_uuid']}",
        )

    #
    # USER...
    # check above
    #
    resp = request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/tms/taskforces/find",
        {
            "query": {
                "task_id": task_id,
            },
            "projection": ["tms_status"],
        },
    )
    assert len(resp["taskforces"]) == len(condor_locs_w_jel)
    assert all(tf["tms_status"] == "condor-rm" for tf in resp["taskforces"])


def tms_condor_clusters_done(
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
        resp = request_and_validate(
            rc,
            openapi_spec,
            "POST",
            "/tms/taskforces/find",
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
        resp = request_and_validate(
            rc,
            openapi_spec,
            "POST",
            f"/tms/taskforce/condor-complete/{resp['taskforces'][0]['taskforce_uuid']}",
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
    resp = request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/tms/taskforces/find",
        {
            "query": {
                "task_id": task_id,
            },
            "projection": ["taskforce_uuid", "tms_status", "condor_complete_ts"],
        },
    )
    assert len(resp["taskforces"]) == len(condor_locs_w_jel)
    assert all(
        (
            tf["tms_status"] == "condor-rm"
            and tf["condor_complete_ts"] == hash(tf["taskforce_uuid"]) % 1700000000
        )
        for tf in resp["taskforces"]
    )
