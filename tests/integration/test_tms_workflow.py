"""Mimic a TMS workflow, hitting the expected REST endpoints."""


import json
import logging
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
CONDOR_LOCATIONS = [("COLLECTOR1", "SCHEDD1"), ("COLLECTOR2", "SCHEDD2")]


# ----------------------------------------------------------------------------


_OPENAPI_JSON = Path(__file__).parent / "../../wms/schema/rest_openapi.json"


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
    print(out)
    return out


# ----------------------------------------------------------------------------


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
    #

    task_directive = request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/task/directive",
        {"foo": 1, "bar": 2},
    )

    resp = request_and_validate(
        rc,
        openapi_spec,
        "GET",
        f"/task/directive/{task_directive['task_id']}",
    )
    assert resp == task_directive

    resp = request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/task/directives/find",
        {"foo": 1, "bar": 2},
    )
    assert len(resp["task_directives"]) == 1
    assert resp["task_directives"][0] == task_directive

    #
    # TMS(es) starter(s)...
    #

    for collector, schedd in CONDOR_LOCATIONS:
        # get next to start
        taskforce = request_and_validate(
            rc,
            openapi_spec,
            "GET",
            "/tms/taskforce/pending",
            {"collector": collector, "schedd": schedd},
        )
        # check that it's not deleted
        resp = request_and_validate(
            rc,
            openapi_spec,
            "GET",
            f"/tms/taskforce/{taskforce['taskforce_uuid']}",
        )
        assert not resp["is_deleted"]
        # confirm it has started
        resp = request_and_validate(
            rc,
            openapi_spec,
            "POST",
            f"/tms/taskforce/running/{taskforce['taskforce_uuid']}",
            {"ewms_taskforce_attrs": 123},
        )

    #
    # USER...
    # check directive reflects startup (runtime-assembled list of taskforces)
    #

    #
    # TMS(es) watcher(s)...
    # no jobs yet (waiting for condor)
    #

    for collector, schedd in CONDOR_LOCATIONS:
        resp = request_and_validate(
            rc,
            openapi_spec,
            "POST",
            "/tms/taskforces/find",
            {
                "filter": {
                    "collector": collector,
                    "schedd": schedd,
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
                "compound_statuses_by_taskforce": {
                    taskforce_uuid: {
                        "started": {"tasked": 15},
                    }
                },
            },
        )
        assert resp["uuids"] == [taskforce_uuid]

    #
    # USER...
    # check above
    #

    #
    # TMS(es) watcher(s)...
    # jobs in action!
    #

    for collector, schedd in CONDOR_LOCATIONS:
        resp = request_and_validate(
            rc,
            openapi_spec,
            "POST",
            "/tms/taskforces/find",
            {
                "filter": {
                    "collector": collector,
                    "schedd": schedd,
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
                "top_task_errors_by_taskforce": {taskforce_uuid: {"too_cool": 3}},
                "compound_statuses_by_taskforce": {
                    taskforce_uuid: {
                        "started": {"tasked": 15},
                        "stopped": {"tasked": 20},
                    }
                },
            },
        )
        assert resp["uuids"] == [taskforce_uuid]

    #
    # USER...
    # check above
    #

    #
    # TMS(es) watcher(s)...
    # jobs done
    #

    for collector, schedd in CONDOR_LOCATIONS:
        resp = request_and_validate(
            rc,
            openapi_spec,
            "POST",
            "/tms/taskforces/find",
            {
                "filter": {
                    "collector": collector,
                    "schedd": schedd,
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
                    taskforce_uuid: {"too_cool": 5, "empty": 1}
                },
                "compound_statuses_by_taskforce": {
                    taskforce_uuid: {
                        "started": {"tasked": 11, "done": 1},
                        "stopped": {"tasked": 50},
                    }
                },
            },
        )
        assert resp["uuids"] == [taskforce_uuid]

    #
    # USER...
    # check jobs done & result
    #

    #
    # TMS(es) stopper(s)...
    #

    for collector, schedd in CONDOR_LOCATIONS:
        # get next to stop
        taskforce = request_and_validate(
            rc,
            openapi_spec,
            "GET",
            "/tms/taskforce/stop",
            {"collector": collector, "schedd": schedd},
        )
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

    #
    # TMS(es) watcher(s)...
    # jel done
    #

    for collector, schedd in CONDOR_LOCATIONS:
        resp = request_and_validate(
            rc,
            openapi_spec,
            "POST",
            "/tms/job-event-log",
            {
                "job_event_log_fpath": JOB_EVENT_LOG_FPATH,
                "collector": collector,
                "schedd": schedd,
                "finished": True,
            },
        )
        # check deleted
        resp = request_and_validate(
            rc,
            openapi_spec,
            "POST",
            "/tms/taskforces/find",
            {
                "filter": {
                    "collector": collector,
                    "schedd": schedd,
                    "job_event_log_fpath": JOB_EVENT_LOG_FPATH,
                },
                "projection": ["taskforce_uuid", "cluster_id"],
            },
        )
        assert len(resp["taskforces"]) == 1
        # TODO - CHECK THAT JEL IS DELETED / FINISHED


# ----------------------------------------------------------------------------
