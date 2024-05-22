"""Common high-level actions that occur in many situations."""

import asyncio
import copy
import json
import logging
import os
from pathlib import Path

import openapi_core
from jsonschema_path import SchemaPath
from rest_tools.client import RestClient
from rest_tools.client.utils import request_and_validate

LOGGER = logging.getLogger(__name__)


_OPENAPI_JSON = (
    Path(__file__).parent / "../../wms/" / os.environ["REST_OPENAPI_SPEC_FPATH"]
)


async def query_for_schema(rc: RestClient) -> openapi_core.OpenAPI:
    resp = await request_and_validate(
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


async def user_requests_new_workflow(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    condor_locations: dict,
) -> str:
    """Return task id."""
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
    environment = {}
    input_files = []

    #
    # USER...
    # requests new task
    #
    workflow_resp = await request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/workflow",
        dict(
            tasks=[
                dict(
                    cluster_locations=list(condor_locations.keys()),
                    task_image=task_image,
                    task_args=task_args,
                    input_queue_aliases=["qfoo"],
                    output_queue_aliases=["qbar"],
                    #
                    n_workers=n_workers,
                    worker_config=worker_config,
                    # environment=environment,  # empty
                    # input_files=input_files,  # empty
                )
            ],
            public_queue_aliases=["qfoo", "qbar"],
        ),
    )
    # TODO - update asserts when/if testing multi-task workflows
    assert len(workflow_resp["task_directives"]) == 1
    assert len(workflow_resp["taskforces"]) == 2

    # query about task directive & its taskforces
    task_directive = workflow_resp["task_directives"][0]
    task_id = task_directive["task_id"]
    resp = await request_and_validate(
        rc,
        openapi_spec,
        "GET",
        f"/task/directive/{task_id}",
    )
    assert resp == task_directive
    resp = await request_and_validate(
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

    # look at taskforces
    resp = await request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/taskforces/find",
        {
            "query": {
                "task_id": task_id,
            },
        },
    )
    assert len(resp["taskforces"]) == len(condor_locations)
    # check locations were translated correctly to collector+schedd
    assert sorted(
        (tf["collector"], tf["schedd"]) for tf in resp["taskforces"]
    ) == sorted((loc["collector"], loc["schedd"]) for loc in condor_locations.values())

    assert all(tf["phase"] == "pre-mq-activation" for tf in resp["taskforces"])

    assert all(tf["worker_config"] == worker_config for tf in resp["taskforces"])
    assert all(tf["n_workers"] == n_workers for tf in resp["taskforces"])
    assert all(
        tf["container_config"]
        == dict(
            image=task_image,
            arguments=task_args,
            environment={
                **environment,
                "EWMS_PILOT_QUEUE_INCOMING": "123qfoo",
                "EWMS_PILOT_QUEUE_OUTGOING": "123qbar",
            },
            input_files=input_files,
        )
        for tf in resp["taskforces"]
    )

    return task_id


async def taskforce_launch_control_marks_taskforces_pending_starter(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    task_id: str,
    n_locations: int,
) -> None:
    """Wait expected time for taskforce_launch_control to set taskforces as 'pending-
    starter'."""
    await asyncio.sleep(int(os.environ["WORKFLOW_MQ_ACTIVATOR_DELAY"]))
    await asyncio.sleep(int(os.environ["TASKFORCE_LAUNCH_CONTROL_DELAY"]) * n_locations)

    resp = await request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/taskforces/find",
        {
            "query": {
                "task_id": task_id,
            },
            "projection": ["phase"],
        },
    )
    assert len(resp["taskforces"]) == n_locations
    LOGGER.debug(resp["taskforces"])
    assert all(tf["phase"] == "pending-starter" for tf in resp["taskforces"])


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
        taskforce = await request_and_validate(
            rc,
            openapi_spec,
            "GET",
            "/taskforce/tms-action/pending-starter",
            {"collector": loc["collector"], "schedd": loc["schedd"]},
        )
        assert taskforce
        taskforce_uuid = taskforce["taskforce_uuid"]
        # check that it's still pending
        resp = await request_and_validate(
            rc,
            openapi_spec,
            "GET",
            f"/taskforce/{taskforce_uuid}",
        )
        assert resp["phase"] == "pending-starter"
        # confirm it has started
        condor_locs_w_jel[shortname]["jel"] = "/home/the_job_event_log_fpath"
        resp = await request_and_validate(
            rc,
            openapi_spec,
            "POST",
            f"/taskforce/tms-action/condor-submit/{taskforce_uuid}",
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
    resp = await request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/taskforces/find",
        {
            "query": {
                "task_id": task_id,
            },
            "projection": ["phase"],
        },
    )
    assert len(resp["taskforces"]) == len(condor_locations)
    assert all(tf["phase"] == "condor-submit" for tf in resp["taskforces"])
    # check directive reflects startup (runtime-assembled list of taskforces)
    resp = await request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/taskforces/find",
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
        resp = await request_and_validate(
            rc,
            openapi_spec,
            "POST",
            "/taskforces/find",
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
        resp = await request_and_validate(
            rc,
            openapi_spec,
            "POST",
            "/taskforces/tms/status",
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
    resp = await request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/taskforces/find",
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


async def user_aborts_workflow(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    task_id: str,
    condor_locations: dict,
    aborted_after_condor: bool = False,
) -> None:
    #
    # USER...
    # stop task
    #
    resp = await request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/workflow/find",
        {
            "query": {"task_id": task_id},
            "projection": ["workflow_id"],
        },
    )
    workflow_id = resp["workflow_id"]
    resp = await request_and_validate(
        rc,
        openapi_spec,
        "DELETE",
        f"/workflow/{workflow_id}",
    )
    assert resp == {
        "workflow_id": workflow_id,
        "n_task_directives": 1,
        "n_taskforces": len(condor_locations) if not aborted_after_condor else 0,
    }
    resp = await request_and_validate(
        rc,
        openapi_spec,
        "GET",
        f"/task/directive/{task_id}",
    )
    assert resp["aborted"] is True


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
        taskforce = await request_and_validate(
            rc,
            openapi_spec,
            "GET",
            "/taskforce/tms-action/pending-stopper",
            {"collector": loc["collector"], "schedd": loc["schedd"]},
        )
        assert taskforce
        # confirm it has stopped
        resp = await request_and_validate(
            rc,
            openapi_spec,
            "DELETE",
            f"/taskforce/tms-action/pending-stopper/{taskforce['taskforce_uuid']}",
        )

    #
    # USER...
    # check above
    #
    resp = await request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/taskforces/find",
        {
            "query": {
                "task_id": task_id,
            },
            "projection": ["phase"],
        },
    )
    assert len(resp["taskforces"]) == len(condor_locations)
    assert all(tf["phase"] == "condor-rm" for tf in resp["taskforces"])


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
        resp = await request_and_validate(
            rc,
            openapi_spec,
            "POST",
            "/taskforces/find",
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
        resp = await request_and_validate(
            rc,
            openapi_spec,
            "POST",
            f"/taskforce/tms/condor-complete/{resp['taskforces'][0]['taskforce_uuid']}",
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
    resp = await request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/taskforces/find",
        {
            "query": {
                "task_id": task_id,
            },
            "projection": ["taskforce_uuid", "condor_complete_ts"],
        },
    )
    assert len(resp["taskforces"]) == len(condor_locs_w_jel)
    assert all(
        tf["condor_complete_ts"] == hash(tf["taskforce_uuid"]) % 1700000000  # see above
        for tf in resp["taskforces"]
    )
