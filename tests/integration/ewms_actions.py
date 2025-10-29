"""Common high-level actions that occur in many situations."""

import json
import logging
import os
import time
from pathlib import Path

import openapi_core
from jsonschema_path import SchemaPath
from rest_tools.client import RestClient
from rest_tools.client.utils import request_and_validate

from .utils import (
    CONDOR_LOCATIONS_LOOKUP,
    StateForTMS,
    _URL_V_PREFIX,
    _request_and_validate_and_print,
    check_taskforce_states,
    sleep_until_background_runners_advance_taskforces,
)

LOGGER = logging.getLogger(__name__)


_OPENAPI_JSON = (
    Path(__file__).parent / "../../wms/" / os.environ["REST_OPENAPI_SPEC_FPATH"]
)


async def query_for_schema(rc: RestClient) -> openapi_core.OpenAPI:
    """Get the OpenAPI schema."""
    resp = await request_and_validate(
        rc,
        # only read json file for this request
        openapi_core.OpenAPI(SchemaPath.from_file_path(str(_OPENAPI_JSON))),
        "GET",
        f"/{_URL_V_PREFIX}/schema/openapi",
    )
    with open(_OPENAPI_JSON, "rb") as f:
        assert json.load(f) == resp
    openapi_spec = openapi_core.OpenAPI(SchemaPath.from_dict(resp))

    return openapi_spec


async def user_requests_new_workflow(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    condor_locations: list[str],
) -> tuple[str, str, list[StateForTMS]]:
    """Return workflow and task ids."""
    task_image = "icecube/earthpassenger"
    task_args = "aaa bbb --ccc 123"
    # no task_env
    init_image = "icecube/spacecaptain"
    # no init_args
    init_env = {"foo": "bar", "baz": "789"}
    n_workers = 99
    worker_config = {
        "do_transfer_worker_stdouterr": False,
        "max_worker_runtime": 60 * 60 * 1,
        "n_cores": 4,
        "priority": 1,
        "worker_disk": "1G",
        "worker_memory": "512M",
        "condor_requirements": "bar && baz",
    }
    pilot_config = {
        "tag": "latest",
        "image_source": "cvmfs",
        "environment": {},
        "input_files": [],
    }

    # so, technically, the tms has not seen these taskforces, but we can pre-assemble
    #   this list to make the tests cleaner
    tms_states = [
        StateForTMS(
            short_name,
            CONDOR_LOCATIONS_LOOKUP[short_name]["schedd"],
            1,
        )
        for short_name in condor_locations
    ]

    #
    # USER...
    # requests new workflow
    #
    workflow_resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "POST",
        f"/{_URL_V_PREFIX}/workflows",
        {
            "tasks": [
                {
                    "cluster_locations": [tmss.shortname for tmss in tms_states],
                    "task_image": task_image,
                    "task_args": task_args,
                    # no task_env
                    "init_image": init_image,
                    # no init_args
                    "init_env": init_env,
                    "input_queue_aliases": ["qfoo"],
                    "output_queue_aliases": ["qbar"],
                    #
                    "n_workers": n_workers,
                    "worker_config": worker_config,
                    "pilot_config": pilot_config,  # optional
                }
            ],
            "public_queue_aliases": ["qfoo", "qbar"],
        },
    )
    # TODO - update asserts when/if testing multi-task workflows
    assert workflow_resp["workflow"]
    assert len(workflow_resp["task_directives"]) == 1
    assert len(workflow_resp["taskforces"]) == 2
    #
    # task_directive checks
    for td in workflow_resp["task_directives"]:
        assert td["task_image"] == task_image
        assert td["task_args"] == task_args
        assert td["task_env"] == {}
        assert td["init_image"] == init_image
        assert td["init_args"] == ""
        assert td["init_env"] == init_env
    #
    # taskforce checks
    assert len(workflow_resp["taskforces"]) == sum(s.n_taskforces for s in tms_states)
    # -- check locations were translated correctly to schedd
    assert sorted(tf["schedd"] for tf in workflow_resp["taskforces"]) == sorted(
        tmss.schedd for tmss in tms_states
    )
    # -- check all collectors are None
    assert all(tf["collector"] is None for tf in workflow_resp["taskforces"])
    # -- other fields
    for tf in workflow_resp["taskforces"]:
        assert tf["phase"] == "pre-mq-activation"
        assert tf["phase_change_log"][-1]["target_phase"] == "pre-mq-activation"
        assert tf["worker_config"] == worker_config
        assert tf["n_workers"] == n_workers
        assert tf["pilot_config"] == {
            **pilot_config,
            **{"tag": os.environ["TEST_PILOT_IMAGE_LATEST_TAG"]},
        }

    #
    # background processes advance taskforces
    #
    await sleep_until_background_runners_advance_taskforces(
        len(workflow_resp["taskforces"])
    )

    #
    # USER...
    # check above

    # query about task directive
    task_directive = workflow_resp["task_directives"][0]
    task_id = task_directive["task_id"]
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "GET",
        f"/{_URL_V_PREFIX}/task-directives/{task_id}",
    )
    assert resp == task_directive
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "POST",
        f"/{_URL_V_PREFIX}/query/task-directives",
        {"query": {"task_id": task_id}},
    )
    assert len(resp["task_directives"]) == 1
    assert resp["task_directives"][0] == task_directive

    # look at taskforces
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        len(workflow_resp["taskforces"]),
        "pending-starter",
        ("pending-starter", True),
    )
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "POST",
        f"/{_URL_V_PREFIX}/query/taskforces",
        {
            "query": {"task_id": task_id},
            "projection": ["pilot_config"],
        },
    )
    assert all(
        tf["pilot_config"]["environment"] == pilot_config["environment"]
        for tf in resp["taskforces"]
    )

    return workflow_resp["workflow"]["workflow_id"], task_id, tms_states


async def tms_starter(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    task_id: str,
    tms_states: list[StateForTMS],
) -> list[StateForTMS]:
    #
    # TMS(es) starter(s)...
    #
    for tmss in tms_states:
        for _ in range(tmss.n_taskforces):
            # get next to start
            resp = await _request_and_validate_and_print(
                rc,
                openapi_spec,
                "GET",
                f"/{_URL_V_PREFIX}/tms/pending-starter/taskforces",
                {"schedd": tmss.schedd},
            )
            assert resp["taskforce"]
            assert resp["task_directive"]
            assert resp["mqprofiles"]
            taskforce_uuid = resp["taskforce"]["taskforce_uuid"]
            # check that it's still pending
            resp = await _request_and_validate_and_print(
                rc,
                openapi_spec,
                "GET",
                f"/{_URL_V_PREFIX}/taskforces/{taskforce_uuid}",
            )
            assert resp["phase"] == "pending-starter"
            # TMS confirms it has started...
            tmss.job_event_log_fpath = "/home/the_job_event_log_fpath"  # keep constant
            resp = await _request_and_validate_and_print(
                rc,
                openapi_spec,
                "POST",
                f"/{_URL_V_PREFIX}/tms/condor-submit/taskforces/{taskforce_uuid}",
                {
                    "cluster_id": 123456,
                    "n_workers": 5600,
                    "submit_dict": {"foo": 123, "bar": "abc"},
                    "job_event_log_fpath": tmss.job_event_log_fpath,
                },
            )

    return tms_states


async def tms_watcher_sends_status_update(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    task_id: str,
    tms_states: list[StateForTMS],
    top_task_errors_by_locshortname: dict,
    compound_statuses_by_locshortname: dict,
) -> None:
    #
    # TMS(es) watcher(s)...
    # jobs in action!
    #
    for tmss in tms_states:  # iterate over the unique tms locations
        resp = await _request_and_validate_and_print(
            rc,
            openapi_spec,
            "POST",
            f"/{_URL_V_PREFIX}/query/taskforces",
            {
                "query": {
                    "schedd": tmss.schedd,
                    "job_event_log_fpath": tmss.job_event_log_fpath,
                },
                "projection": ["taskforce_uuid", "cluster_id"],
            },
        )
        assert len(resp["taskforces"]) == tmss.n_taskforces
        for tf in resp["taskforces"]:
            resp = await _request_and_validate_and_print(
                rc,
                openapi_spec,
                "POST",
                f"/{_URL_V_PREFIX}/tms/statuses/taskforces",
                {
                    "top_task_errors_by_taskforce": {
                        tf["taskforce_uuid"]: top_task_errors_by_locshortname[
                            tmss.shortname
                        ],
                    },
                    "compound_statuses_by_taskforce": {
                        tf["taskforce_uuid"]: compound_statuses_by_locshortname[
                            tmss.shortname
                        ]
                    },
                },
            )
            assert resp["results"] == [
                {"uuid": tf["taskforce_uuid"], "status": "updated"}
            ]

    #
    # USER...
    # check above
    #
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "POST",
        f"/{_URL_V_PREFIX}/query/taskforces",
        {
            "query": {"task_id": task_id},
            "projection": [
                "taskforce_uuid",
                "compound_statuses",
                "top_task_errors",
                "schedd",
            ],
        },
    )
    assert len(resp["taskforces"]) == sum(s.n_taskforces for s in tms_states)
    for tf in resp["taskforces"]:
        for tmss in tms_states:
            if tmss.schedd == tf["schedd"]:
                break
        else:
            assert 0  # -> did not find it
        # fmt: off
        # has new vals
        assert tf["compound_statuses"] == compound_statuses_by_locshortname[tmss.shortname]
        assert tf["top_task_errors"] == top_task_errors_by_locshortname[tmss.shortname]
        # fmt: on


async def user_deactivates_workflow(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    kind_of_deactivation: str,
    task_id: str,
    n_taskforces_stopped: int,
) -> None:
    #
    # USER...
    # stop workflow
    #
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "POST",
        f"/{_URL_V_PREFIX}/query/task-directives",
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
                "ABORTED": f"/{_URL_V_PREFIX}/workflows/{workflow_id}/actions/abort",
                "FINISHED": f"/{_URL_V_PREFIX}/workflows/{workflow_id}/actions/finished",
            }[kind_of_deactivation]
        ),
    )
    assert resp == {
        "workflow_id": workflow_id,
        "n_taskforces": n_taskforces_stopped,
    }
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "GET",
        f"/{_URL_V_PREFIX}/workflows/{workflow_id}",
    )
    assert resp["deactivated"] == kind_of_deactivation
    assert then < resp["deactivated_ts"] < time.time()

    if not n_taskforces_stopped:
        return

    #
    # USER...
    # check above
    #
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        n_taskforces_stopped,
        "pending-stopper",
        ("pending-stopper", True),
    )


async def tms_stopper(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    task_id: str,
    tms_states: list[StateForTMS],
) -> None:
    #
    # TMS(es) stopper(s)...
    # this happens even if task aborted before condor
    #
    for tmss in tms_states:
        for _ in range(tmss.n_taskforces):
            # get next to stop
            taskforce = await _request_and_validate_and_print(
                rc,
                openapi_spec,
                "GET",
                f"/{_URL_V_PREFIX}/tms/pending-stopper/taskforces",
                {"schedd": tmss.schedd},
            )
            assert taskforce
            # confirm it has stopped
            await _request_and_validate_and_print(
                rc,
                openapi_spec,
                "POST",
                f"/{_URL_V_PREFIX}/tms/condor-rm/taskforces/{taskforce['taskforce_uuid']}",
            )

    #
    # USER...
    # check above
    #
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "condor-rm",
        ("condor-rm", True),
    )


async def tms_condor_clusters_done(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    task_id: str,
    tms_states: list[StateForTMS],
) -> None:
    #
    # TMS(es) watcher(s)...
    # taskforces' condor clusters are done
    #
    for tmss in tms_states:
        resp = await _request_and_validate_and_print(
            rc,
            openapi_spec,
            "POST",
            f"/{_URL_V_PREFIX}/query/taskforces",
            {
                "query": {
                    "schedd": tmss.schedd,
                    "job_event_log_fpath": tmss.job_event_log_fpath,
                },
                "projection": ["taskforce_uuid"],
            },
        )
        assert len(resp["taskforces"]) == tmss.n_taskforces
        for tf in resp["taskforces"]:
            resp = await _request_and_validate_and_print(
                rc,
                openapi_spec,
                "POST",
                f"/{_URL_V_PREFIX}/tms/condor-complete/taskforces/{tf['taskforce_uuid']}",
                {
                    "condor_complete_ts": (
                        # NOTE: need a unique timestamp that we don't need to rely on the timing of this test
                        hash(tf["taskforce_uuid"])
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
        f"/{_URL_V_PREFIX}/query/taskforces",
        {
            "query": {
                "task_id": task_id,
            },
            "projection": ["taskforce_uuid", "phase_change_log"],
        },
    )
    assert len(resp["taskforces"]) == sum(s.n_taskforces for s in tms_states)
    assert all(
        list(
            pcl["source_event_time"]
            for pcl in tf["phase_change_log"]
            if pcl["target_phase"] == "condor-complete"
        )  # this will also check if there is only 1 matching entry
        == [hash(tf["taskforce_uuid"]) % 1700000000]  # see above
        for tf in resp["taskforces"]
    )


async def add_more_workers(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    task_id: str,
    cluster_location: str,
    tms_states: list[StateForTMS],
) -> list[StateForTMS]:

    # get total -- used at the very end of func
    total_n_taskforces = len(
        (
            await _request_and_validate_and_print(
                rc,
                openapi_spec,
                "POST",
                f"/{_URL_V_PREFIX}/query/taskforces",
                {"query": {"task_id": task_id}},
            )
        )["taskforces"]
    )
    assert total_n_taskforces == sum(tms.n_taskforces for tms in tms_states)

    # grab the existing taskforce at the location
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "POST",
        f"/{_URL_V_PREFIX}/query/taskforces",
        {
            "query": {
                "task_id": task_id,
                "schedd": CONDOR_LOCATIONS_LOOKUP[cluster_location]["schedd"],
            },
        },
    )
    assert len(resp["taskforces"]) == next(
        tms.n_taskforces for tms in tms_states if tms.shortname == cluster_location
    )
    existing_tf = resp["taskforces"][0]

    #
    # USER or TMS...
    # make another taskforce for the task directive
    #
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "POST",
        f"/{_URL_V_PREFIX}/task-directives/{task_id}/actions/add-workers",
        {
            "cluster_location": cluster_location,
            "n_workers": 100,
        },
    )
    taskforce_uuid = resp["taskforce_uuid"]
    expected = {
        **existing_tf,  # near duplicate with a few differences
        **{
            "taskforce_uuid": taskforce_uuid,  # iow don't check
            "timestamp": resp["timestamp"],  # iow don't check
            "priority": existing_tf["priority"] + 100,  # bumped by the handler
            "n_workers": resp["n_workers"],  # iow don't check
            #
            # these are only set once the TMS picks up the TF
            "cluster_id": None,
            "submit_dict": {},
            "job_event_log_fpath": "",
            "compound_statuses": {},
            "top_task_errors": {},
            #
            "phase": "pre-mq-activation",
            "phase_change_log": [
                {
                    "target_phase": "pre-mq-activation",
                    "timestamp": resp["phase_change_log"][0]["timestamp"],  # dont check
                    "source_event_time": None,
                    "was_successful": True,
                    "source_entity": "USER",
                    "context": "Created when adding more workers for this task directive.",
                }
            ],
        },
    }
    print("expected:", expected)
    assert resp == expected

    # check that there are 2 taskforces at location now
    resp = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "POST",
        f"/{_URL_V_PREFIX}/query/taskforces",
        {
            "query": {
                "task_id": task_id,
                "schedd": CONDOR_LOCATIONS_LOOKUP[cluster_location]["schedd"],
            },
        },
    )
    assert (
        len(resp["taskforces"])
        == next(
            tms.n_taskforces for tms in tms_states if tms.shortname == cluster_location
        )
        + 1
    )

    # check total only increased by 1 -- iow, the taskforce was only added to the 1 location
    new_total_n_taskforces = len(
        (
            await _request_and_validate_and_print(
                rc,
                openapi_spec,
                "POST",
                f"/{_URL_V_PREFIX}/query/taskforces",
                {"query": {"task_id": task_id}},
            )
        )["taskforces"]
    )
    assert new_total_n_taskforces == total_n_taskforces + 1

    #
    # background processes advance taskforces
    #
    await sleep_until_background_runners_advance_taskforces(1)
    # check above
    tf = await _request_and_validate_and_print(
        rc,
        openapi_spec,
        "GET",
        f"/{_URL_V_PREFIX}/taskforces/{taskforce_uuid}",
    )
    assert tf["phase"] == "pending-starter"
    assert tf["phase_change_log"][-1]["target_phase"] == "pending-starter"
    assert tf["phase_change_log"][-1]["was_successful"] is True

    # increment count then return
    for tmss in tms_states:
        if tmss.shortname == cluster_location:
            tmss.n_taskforces += 1
    return tms_states
