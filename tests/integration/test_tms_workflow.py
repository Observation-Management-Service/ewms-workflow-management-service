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

import ewms_actions

LOGGER = logging.getLogger(__name__)


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
    openapi_spec = ewms_actions.query_for_schema(rc)

    task_id = ewms_actions.user_requests_new_task(
        rc,
        openapi_spec,
        list(CONDOR_LOCATIONS.keys()),
    )

    condor_locs_w_jel = ewms_actions.tms_starter(
        rc,
        openapi_spec,
        task_id,
        CONDOR_LOCATIONS,
    )

    ewms_actions.tms_watcher__with_jobs(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__1,
        COMPOUND_STATUSES__1,
    )

    ewms_actions.tms_watcher__with_jobs(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__2,
        COMPOUND_STATUSES__2,
    )

    ewms_actions.tms_watcher__with_jobs(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__3,
        COMPOUND_STATUSES__3,
    )

    ewms_actions.user_aborts_task(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
    )

    ewms_actions.tms_condor_clusters_done(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
    )


# ----------------------------------------------------------------------------
