"""Mimic a TMS workflow, hitting the expected REST endpoints."""


import json
import logging
import os
from pathlib import Path
from typing import Any

import openapi_core
import requests
from jsonschema_path import SchemaPath
from openapi_core.contrib import requests as openapi_core_requests
from rest_tools.client import RestClient

LOGGER = logging.getLogger(__name__)
logging.getLogger("parse").setLevel(logging.INFO)


JOB_EVENT_LOG_FPATH = "/home/the_job_event_log_fpath"
CONDOR_LOCATIONS = {
    "test-alpha": {
        "collector": "COLLECTOR1",
        "schedd": "SCHEDD1",
    },
    "test-beta": {
        "collector": "COLLECTOR2",
        "schedd": "SCHEDD2",
    },
}


def _collector_schedd_to_location(collector: str, schedd: str) -> str:
    for lname, loc in CONDOR_LOCATIONS.items():
        if loc["collector"] == collector and loc["schedd"] == schedd:
            return lname
    raise ValueError(f"Location not found: {collector=} {schedd=}")


# ----------------------------------------------------------------------------


_OPENAPI_JSON = (
    Path(__file__).parent / "../../wms/" / os.environ["REST_OPENAPI_SPEC_FPATH"]
)


def request_and_validate(
    rc: RestClient,
    openapi_spec: openapi_core.OpenAPI,
    method: str,
    path: str,
    args: dict[str, Any] | None = None,
) -> Any:
    """Make request and validate the response."""
    url, kwargs = rc._prepare(method, path, args=args)
    response = requests.request(method, url, **kwargs)

    # duck typing magic
    class _DuckResponse(openapi_core.protocols.Response):
        """AKA 'openapi_core_requests.RequestsOpenAPIResponse' but correct."""

        @property
        def data(self) -> bytes | None:
            return response.content

        @property
        def status_code(self) -> int:
            return int(response.status_code)

        @property
        def content_type(self) -> str:
            # application/json; charset=UTF-8  ->  application/json
            # ex: openapi_core.validation.response.exceptions.DataValidationError: DataValidationError: Content for the following mimetype not found: application/json; charset=UTF-8. Valid mimetypes: ['application/json']
            return str(response.headers.get("Content-Type", "")).split(";")[0]
            # alternatively, look at how 'openapi_core_requests.RequestsOpenAPIRequest.mimetype' handles similarly

        @property
        def headers(self) -> dict:
            return dict(response.headers)

    openapi_spec.validate_response(
        openapi_core_requests.RequestsOpenAPIRequest(response.request),
        _DuckResponse(),
    )

    out = rc._decode(response.content)
    response.raise_for_status()
    if path != "/schema/openapi":
        print(out)
    return out


# ----------------------------------------------------------------------------

COMPOUND_STATUSES__1 = {  # type: ignore[var-annotated]
    "test-alpha": {},
    "test-beta": {},
}
TOP_TASK_ERRORS__1 = {  # type: ignore[var-annotated]
    "test-alpha": {},
    "test-beta": {},
}
#
COMPOUND_STATUSES__2 = {
    "test-alpha": {
        "started": {"tasked": 256},
    },
    "test-beta": {
        "started": {"tasked": 150},
        "stopped": {"tasked": 2000},
    },
}
TOP_TASK_ERRORS__2 = {
    "test-alpha": {
        "too_cool": 326,
    },
    "test-beta": {
        "too_warm": 453,
    },
}
#
COMPOUND_STATUSES__3 = {
    "test-alpha": {
        "started": {"tasked": 1126, "done": 1265},
        "stopped": {"tasked": 502},
    },
    "test-beta": {
        "started": {"pre-tasked": 811, "done": 135},
        "stopped": {"tasked": 560},
    },
}
TOP_TASK_ERRORS__3 = {
    "test-alpha": {
        "too_cool": 5156,
        "full": 123,
    },
    "test-beta": {
        "too_cool": 1565,
        "empty": 861,
    },
}


async def test_000(rc: RestClient) -> None:
    """Regular workflow."""
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
            "cluster_locations": list(CONDOR_LOCATIONS.keys()),
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
    assert len(resp["taskforces"]) == len(CONDOR_LOCATIONS)
    assert all(tf["tms_status"] == "pending-start" for tf in resp["taskforces"])

    #
    # TMS(es) starter(s)...
    #
    for loc in CONDOR_LOCATIONS.values():
        # get next to start
        taskforce = request_and_validate(
            rc,
            openapi_spec,
            "GET",
            "/tms/taskforce/pending",
            {"collector": loc["collector"], "schedd": loc["schedd"]},
        )
        assert taskforce
        # check that it's still pending
        resp = request_and_validate(
            rc,
            openapi_spec,
            "GET",
            f"/tms/taskforce/{taskforce['taskforce_uuid']}",
        )
        assert resp["tms_status"] == "pending-start"
        # confirm it has started
        resp = request_and_validate(
            rc,
            openapi_spec,
            "POST",
            f"/tms/taskforce/running/{taskforce['taskforce_uuid']}",
            {
                "cluster_id": 123456,
                "n_workers": 5600,
                "submit_dict": {"foo": 123, "bar": "abc"},
                "job_event_log_fpath": JOB_EVENT_LOG_FPATH,
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
    assert len(resp["taskforces"]) == len(CONDOR_LOCATIONS)
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
    assert len(resp["taskforces"]) == len(CONDOR_LOCATIONS)
    for loc in CONDOR_LOCATIONS.values():
        assert {"collector": loc["collector"], "schedd": loc["schedd"]} in resp[
            "taskforces"
        ]

    #
    # TMS(es) watcher(s)...
    # no jobs yet (waiting for condor)
    #
    for lname, loc in CONDOR_LOCATIONS.items():
        resp = request_and_validate(
            rc,
            openapi_spec,
            "POST",
            "/tms/taskforces/find",
            {
                "query": {
                    "collector": loc["collector"],
                    "schedd": loc["schedd"],
                    "job_event_log_fpath": JOB_EVENT_LOG_FPATH,
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
                "compound_statuses_by_taskforce": COMPOUND_STATUSES__1[lname],
            },
        )
        assert not resp["taskforce_uuids"]

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
                "compound_statuses_by_taskforce",
                "top_task_errors_by_taskforce",
                "collector",
                "schedd",
            ],
        },
    )
    assert len(resp["taskforces"]) == len(CONDOR_LOCATIONS)
    for tf in resp["taskforces"]:
        lname = _collector_schedd_to_location(tf["collector"], tf["schedd"])
        assert tf["compound_statuses"] == COMPOUND_STATUSES__1[lname]
        assert tf["top_task_errors"] == TOP_TASK_ERRORS__1[lname]

    #
    # TMS(es) watcher(s)...
    # jobs in action!
    #
    for lname, loc in CONDOR_LOCATIONS.items():
        resp = request_and_validate(
            rc,
            openapi_spec,
            "POST",
            "/tms/taskforces/find",
            {
                "query": {
                    "collector": loc["collector"],
                    "schedd": loc["schedd"],
                    "job_event_log_fpath": JOB_EVENT_LOG_FPATH,
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
                    taskforce_uuid: TOP_TASK_ERRORS__2[lname],
                },
                "compound_statuses_by_taskforce": {
                    taskforce_uuid: COMPOUND_STATUSES__2[lname]
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
                "compound_statuses_by_taskforce",
                "top_task_errors_by_taskforce",
                "collector",
                "schedd",
            ],
        },
    )
    assert len(resp["taskforces"]) == len(CONDOR_LOCATIONS)
    for tf in resp["taskforces"]:
        lname = _collector_schedd_to_location(tf["collector"], tf["schedd"])
        assert tf["compound_statuses"] == COMPOUND_STATUSES__2[lname]
        assert tf["top_task_errors"] == TOP_TASK_ERRORS__2[lname]

    #
    # TMS(es) watcher(s)...
    # jobs done
    #
    for lname, loc in CONDOR_LOCATIONS.items():
        resp = request_and_validate(
            rc,
            openapi_spec,
            "POST",
            "/tms/taskforces/find",
            {
                "query": {
                    "collector": loc["collector"],
                    "schedd": loc["schedd"],
                    "job_event_log_fpath": JOB_EVENT_LOG_FPATH,
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
                    taskforce_uuid: TOP_TASK_ERRORS__3[lname],
                },
                "compound_statuses_by_taskforce": {
                    taskforce_uuid: COMPOUND_STATUSES__3[lname]
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
                "compound_statuses_by_taskforce",
                "top_task_errors_by_taskforce",
                "collector",
                "schedd",
            ],
        },
    )
    assert len(resp["taskforces"]) == len(CONDOR_LOCATIONS)
    for tf in resp["taskforces"]:
        lname = _collector_schedd_to_location(tf["collector"], tf["schedd"])
        assert tf["compound_statuses"] == COMPOUND_STATUSES__3[lname]
        assert tf["top_task_errors"] == TOP_TASK_ERRORS__3[lname]

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
    assert resp == {"task_id": task_id, "n_taskforces": len(CONDOR_LOCATIONS)}
    resp = request_and_validate(
        rc,
        openapi_spec,
        "GET",
        f"/task/directive/{task_id}",
    )
    assert resp["terminated"] is True
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
    assert len(resp["taskforces"]) == len(CONDOR_LOCATIONS)
    assert all(tf["tms_status"] == "pending-stop" for tf in resp["taskforces"])

    #
    # TMS(es) stopper(s)...
    #
    for loc in CONDOR_LOCATIONS.values():
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
    assert len(resp["taskforces"]) == len(CONDOR_LOCATIONS)
    assert all(tf["tms_status"] == "condor-rm" for tf in resp["taskforces"])

    #
    # TMS(es) watcher(s)...
    # jel done
    #
    for loc in CONDOR_LOCATIONS.values():
        # TODO -- rethink intention of /tms/job-event-log
        # should instead the tms ask wms if there are anymore pending tasks for this jel?
        # where is the SOT? condor, backlogger, wms?
        # relatedly, are all tasks 'terminated'? if so, then wms is SOT.
        # if not, then there can be lingering jobs (so condor is SOT...?)

        resp = request_and_validate(
            rc,
            openapi_spec,
            "POST",
            "/tms/job-event-log",
            {
                "job_event_log_fpath": JOB_EVENT_LOG_FPATH,
                "collector": loc["collector"],
                "schedd": loc["schedd"],
                "finished": True,
            },
        )
        # TODO - CHECK THAT JEL IS DELETED / FINISHED


# ----------------------------------------------------------------------------
