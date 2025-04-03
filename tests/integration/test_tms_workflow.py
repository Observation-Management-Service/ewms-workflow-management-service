"""Mimic a TMS workflow, hitting the expected REST endpoints."""

import logging
import re
from dataclasses import asdict

import pytest
import requests
from rest_tools.client import RestClient

from . import ewms_actions
from .utils import (
    CONDOR_LOCATIONS_LOOKUP,
    StateForTMS,
    check_nothing_to_start,
    check_nothing_to_stop,
    check_taskforce_states,
    check_workflow_deactivation,
)

LOGGER = logging.getLogger(__name__)


# --------------------------------------------------------------------------------------


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


# --------------------------------------------------------------------------------------


async def test_000(rc: RestClient) -> None:
    """Regular workflow."""
    openapi_spec = await ewms_actions.query_for_schema(rc)

    workflow_id, task_id, tms_states = await ewms_actions.user_requests_new_workflow(
        rc,
        openapi_spec,
        list(CONDOR_LOCATIONS_LOOKUP.keys()),
    )

    # TMS STARTS TASKFORCES!
    tms_states = await ewms_actions.tms_starter(
        rc,
        openapi_spec,
        task_id,
        tms_states,
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "condor-submit",
        ("condor-submit", True),
    )

    # SEND UPDATES FROM TMS (JEL)!
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__1,
        COMPOUND_STATUSES__1,
    )
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__2,
        COMPOUND_STATUSES__2,
    )
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__3,
        COMPOUND_STATUSES__3,
    )

    # CONDOR CLUSTERS FINISH UP!
    await ewms_actions.tms_condor_clusters_done(
        rc,
        openapi_spec,
        task_id,
        tms_states,
    )

    # CHECK FINAL STATES...
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "condor-complete",
        ("condor-complete", True),
    )
    await check_workflow_deactivation(
        rc,
        openapi_spec,
        workflow_id,
        None,
    )

    # in a complete workflow, the user would then 'finish' the workflow
    #   -> this is tested in the 1XX-tests


# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "kind_of_deactivation",
    ["ABORTED", "FINISHED"],
)
async def test_100__deactivated_before_condor(
    rc: RestClient, kind_of_deactivation: str
) -> None:
    """Deactivated workflow (see param for kind_of_deactivation)."""
    openapi_spec = await ewms_actions.query_for_schema(rc)

    workflow_id, task_id, tms_states = await ewms_actions.user_requests_new_workflow(
        rc,
        openapi_spec,
        list(CONDOR_LOCATIONS_LOOKUP.keys()),
    )

    # DEACTIVATE!
    await ewms_actions.user_deactivates_workflow(
        rc,
        openapi_spec,
        kind_of_deactivation,
        task_id,
        sum(s.n_taskforces for s in tms_states),
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "pending-stopper",
        ("pending-stopper", True),
    )
    await check_nothing_to_start(rc, openapi_spec, CONDOR_LOCATIONS_LOOKUP)
    await check_nothing_to_stop(rc, openapi_spec, CONDOR_LOCATIONS_LOOKUP)
    await check_nothing_to_start(rc, openapi_spec, CONDOR_LOCATIONS_LOOKUP)

    # NOTE - since the taskforce(s) aren't started, there are no updates from a JEL

    # tms_states = await ewms_actions.tms_starter(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     CONDOR_LOCATIONS,
    # )

    # # SEND UPDATES FROM TMS (JEL)!
    # await ewms_actions.tms_watcher_sends_status_update(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     tms_states,
    #     TOP_TASK_ERRORS__1,
    #     COMPOUND_STATUSES__1,
    # )
    # await ewms_actions.tms_watcher_sends_status_update(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     tms_states,
    #     TOP_TASK_ERRORS__2,
    #     COMPOUND_STATUSES__2,
    # )
    # await ewms_actions.tms_watcher_sends_status_update(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     tms_states,
    #     TOP_TASK_ERRORS__3,
    #     COMPOUND_STATUSES__3,
    # )

    # await ewms_actions.tms_condor_clusters_done(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     tms_states,
    # )

    # CHECK FINAL STATES...
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "pending-stopper",
        ("pending-stopper", True),
    )
    await check_workflow_deactivation(
        rc,
        openapi_spec,
        workflow_id,
        kind_of_deactivation,
    )


@pytest.mark.parametrize(
    "kind_of_deactivation",
    ["ABORTED", "FINISHED"],
)
async def test_101__deactivated_before_condor(
    rc: RestClient, kind_of_deactivation: str
) -> None:
    """Deactivated workflow (see param for kind_of_deactivation)."""
    openapi_spec = await ewms_actions.query_for_schema(rc)

    workflow_id, task_id, tms_states = await ewms_actions.user_requests_new_workflow(
        rc,
        openapi_spec,
        list(CONDOR_LOCATIONS_LOOKUP.keys()),
    )

    # DEACTIVATE!
    await ewms_actions.user_deactivates_workflow(
        rc,
        openapi_spec,
        kind_of_deactivation,
        task_id,
        sum(s.n_taskforces for s in tms_states),
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "pending-stopper",
        ("pending-stopper", True),
    )
    await check_nothing_to_start(rc, openapi_spec, CONDOR_LOCATIONS_LOOKUP)
    await check_nothing_to_stop(rc, openapi_spec, CONDOR_LOCATIONS_LOOKUP)
    await check_nothing_to_start(rc, openapi_spec, CONDOR_LOCATIONS_LOOKUP)

    # await ewms_actions.taskforce_launch_control_marks_taskforces_pending_starter(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     len(CONDOR_LOCATIONS),
    # )

    # NOTE - since the taskforce(s) aren't started, there are no updates from a JEL

    # tms_states = await ewms_actions.tms_starter(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     CONDOR_LOCATIONS,
    # )

    # # SEND UPDATES FROM TMS (JEL)!
    # await ewms_actions.tms_watcher_sends_status_update(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     tms_states,
    #     TOP_TASK_ERRORS__1,
    #     COMPOUND_STATUSES__1,
    # )
    # await ewms_actions.tms_watcher_sends_status_update(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     tms_states,
    #     TOP_TASK_ERRORS__2,
    #     COMPOUND_STATUSES__2,
    # )
    # await ewms_actions.tms_watcher_sends_status_update(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     tms_states,
    #     TOP_TASK_ERRORS__3,
    #     COMPOUND_STATUSES__3,
    # )

    # await ewms_actions.tms_condor_clusters_done(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     tms_states,
    # )

    # CHECK FINAL STATES...
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "pending-stopper",
        ("pending-stopper", True),
    )
    await check_workflow_deactivation(
        rc,
        openapi_spec,
        workflow_id,
        kind_of_deactivation,
    )


@pytest.mark.parametrize(
    "kind_of_deactivation",
    ["ABORTED", "FINISHED"],
)
async def test_110__deactivated_during_condor(
    rc: RestClient, kind_of_deactivation: str
) -> None:
    """Deactivated workflow (see param for kind_of_deactivation)."""
    openapi_spec = await ewms_actions.query_for_schema(rc)

    workflow_id, task_id, tms_states = await ewms_actions.user_requests_new_workflow(
        rc,
        openapi_spec,
        list(CONDOR_LOCATIONS_LOOKUP.keys()),
    )

    # TMS STARTS TASKFORCES!
    tms_states = await ewms_actions.tms_starter(
        rc,
        openapi_spec,
        task_id,
        tms_states,
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "condor-submit",
        ("condor-submit", True),
    )

    # SEND UPDATES FROM TMS (JEL)!
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__1,
        COMPOUND_STATUSES__1,
    )

    # DEACTIVATE!
    await ewms_actions.user_deactivates_workflow(
        rc,
        openapi_spec,
        kind_of_deactivation,
        task_id,
        sum(s.n_taskforces for s in tms_states),
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "pending-stopper",
        ("pending-stopper", True),
    )
    await ewms_actions.tms_stopper(
        rc,
        openapi_spec,
        task_id,
        tms_states,
    )

    # continue, SEND UPDATES FROM TMS (JEL)
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__2,
        COMPOUND_STATUSES__2,
    )
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__3,
        COMPOUND_STATUSES__3,
    )

    # CONDOR CLUSTERS FINISH UP!
    await ewms_actions.tms_condor_clusters_done(
        rc,
        openapi_spec,
        task_id,
        tms_states,
    )

    # CHECK FINAL STATES...
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "condor-complete",
        ("condor-complete", True),
    )
    await check_workflow_deactivation(
        rc,
        openapi_spec,
        workflow_id,
        kind_of_deactivation,
    )


@pytest.mark.parametrize(
    "kind_of_deactivation",
    ["ABORTED", "FINISHED"],
)
async def test_111__deactivated_during_condor(
    rc: RestClient, kind_of_deactivation: str
) -> None:
    """Deactivated workflow (see param for kind_of_deactivation)."""
    openapi_spec = await ewms_actions.query_for_schema(rc)

    workflow_id, task_id, tms_states = await ewms_actions.user_requests_new_workflow(
        rc,
        openapi_spec,
        list(CONDOR_LOCATIONS_LOOKUP.keys()),
    )

    # TMS STARTS TASKFORCES!
    tms_states = await ewms_actions.tms_starter(
        rc,
        openapi_spec,
        task_id,
        tms_states,
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "condor-submit",
        ("condor-submit", True),
    )

    # SEND UPDATES FROM TMS (JEL)!
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__1,
        COMPOUND_STATUSES__1,
    )
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__2,
        COMPOUND_STATUSES__2,
    )
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__3,
        COMPOUND_STATUSES__3,
    )

    # DEACTIVATE!
    await ewms_actions.user_deactivates_workflow(
        rc,
        openapi_spec,
        kind_of_deactivation,
        task_id,
        sum(s.n_taskforces for s in tms_states),
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "pending-stopper",
        ("pending-stopper", True),
    )
    await ewms_actions.tms_stopper(
        rc,
        openapi_spec,
        task_id,
        tms_states,
    )

    # CONDOR CLUSTERS FINISH UP!
    await ewms_actions.tms_condor_clusters_done(
        rc,
        openapi_spec,
        task_id,
        tms_states,
    )

    # CHECK FINAL STATES...
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "condor-complete",
        ("condor-complete", True),
    )
    await check_workflow_deactivation(
        rc,
        openapi_spec,
        workflow_id,
        kind_of_deactivation,
    )


@pytest.mark.parametrize(
    "kind_of_deactivation",
    ["ABORTED", "FINISHED"],
)
async def test_120__deactivated_after_condor(
    rc: RestClient, kind_of_deactivation: str
) -> None:
    """Deactivated workflow (see param for kind_of_deactivation)."""
    openapi_spec = await ewms_actions.query_for_schema(rc)

    workflow_id, task_id, tms_states = await ewms_actions.user_requests_new_workflow(
        rc,
        openapi_spec,
        list(CONDOR_LOCATIONS_LOOKUP.keys()),
    )

    # TMS STARTS TASKFORCES!
    tms_states = await ewms_actions.tms_starter(
        rc,
        openapi_spec,
        task_id,
        tms_states,
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "condor-submit",
        ("condor-submit", True),
    )

    # SEND UPDATES FROM TMS (JEL)!
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__1,
        COMPOUND_STATUSES__1,
    )
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__2,
        COMPOUND_STATUSES__2,
    )
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__3,
        COMPOUND_STATUSES__3,
    )

    # CONDOR CLUSTERS FINISH UP!
    await ewms_actions.tms_condor_clusters_done(
        rc,
        openapi_spec,
        task_id,
        tms_states,
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "condor-complete",
        ("condor-complete", True),
    )

    # DEACTIVATE!
    await ewms_actions.user_deactivates_workflow(
        rc,
        openapi_spec,
        kind_of_deactivation,
        task_id,
        0,  # no taskforces will actually need to be stopped
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "condor-complete",
        ("pending-stopper", False),
    )
    await check_nothing_to_stop(rc, openapi_spec, CONDOR_LOCATIONS_LOOKUP)

    # CHECK FINAL STATES...
    # NOTE: ^^^ already checked final taskforce states above
    # workflow:
    await check_workflow_deactivation(
        rc,
        openapi_spec,
        workflow_id,
        kind_of_deactivation,
    )


# --------------------------------------------------------------------------------------


async def test_200__add_workers_before_condor(rc: RestClient) -> None:
    """Add workers to workflow."""
    openapi_spec = await ewms_actions.query_for_schema(rc)

    workflow_id, task_id, tms_states = await ewms_actions.user_requests_new_workflow(
        rc,
        openapi_spec,
        list(CONDOR_LOCATIONS_LOOKUP.keys()),
    )

    # ADD MORE WORKERS!
    tms_states = await ewms_actions.add_more_workers(
        rc,
        openapi_spec,
        task_id,
        tms_states[0].shortname,  # add to this location
        tms_states,
    )

    # TMS STARTS TASKFORCES!
    tms_states = await ewms_actions.tms_starter(
        rc,
        openapi_spec,
        task_id,
        tms_states,
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "condor-submit",
        ("condor-submit", True),
    )

    # SEND UPDATES FROM TMS (JEL)!
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__1,
        COMPOUND_STATUSES__1,
    )
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__2,
        COMPOUND_STATUSES__2,
    )
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__3,
        COMPOUND_STATUSES__3,
    )

    # USER FINISHES WORKFLOW
    await ewms_actions.user_deactivates_workflow(
        rc,
        openapi_spec,
        "FINISHED",
        task_id,
        sum(s.n_taskforces for s in tms_states),
    )

    # CONDOR CLUSTERS FINISH UP!
    await ewms_actions.tms_condor_clusters_done(
        rc,
        openapi_spec,
        task_id,
        tms_states,
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "condor-complete",
        ("condor-complete", True),
    )

    # CHECK FINAL STATES...
    # NOTE: ^^^ already checked final taskforce states above
    # workflow:
    await check_workflow_deactivation(
        rc,
        openapi_spec,
        workflow_id,
        "FINISHED",
    )


async def test_210__add_workers_during_condor(rc: RestClient) -> None:
    """Add workers to workflow."""
    openapi_spec = await ewms_actions.query_for_schema(rc)

    workflow_id, task_id, tms_states = await ewms_actions.user_requests_new_workflow(
        rc,
        openapi_spec,
        list(CONDOR_LOCATIONS_LOOKUP.keys()),
    )

    # TMS STARTS TASKFORCES!
    tms_states = await ewms_actions.tms_starter(
        rc,
        openapi_spec,
        task_id,
        tms_states,
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "condor-submit",
        ("condor-submit", True),
    )

    # SEND UPDATES FROM TMS (JEL)!
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__1,
        COMPOUND_STATUSES__1,
    )
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__2,
        COMPOUND_STATUSES__2,
    )
    # ADD MORE WORKERS!
    tms_states = await ewms_actions.add_more_workers(
        rc,
        openapi_spec,
        task_id,
        tms_states[0].shortname,  # add to this location
        tms_states,
    )
    _ = await ewms_actions.tms_starter(  # don't keep the return val -- its an incomplete list
        rc,
        openapi_spec,
        task_id,
        [  # include just the newbie, aka with n_taskforces=1
            StateForTMS(**{**asdict(tms_states[0]), **{"n_taskforces": 1}})
        ],
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "condor-submit",
        ("condor-submit", True),
    )
    # SEND MORE UPDATES FROM TMS (JEL)!
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__3,
        COMPOUND_STATUSES__3,
    )

    # USER FINISHES WORKFLOW
    await ewms_actions.user_deactivates_workflow(
        rc,
        openapi_spec,
        "FINISHED",
        task_id,
        sum(s.n_taskforces for s in tms_states),
    )

    # CONDOR CLUSTERS FINISH UP!
    await ewms_actions.tms_condor_clusters_done(
        rc,
        openapi_spec,
        task_id,
        tms_states,
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "condor-complete",
        ("condor-complete", True),
    )

    # CHECK FINAL STATES...
    # NOTE: ^^^ already checked final taskforce states above
    # workflow:
    await check_workflow_deactivation(
        rc,
        openapi_spec,
        workflow_id,
        "FINISHED",
    )


async def test_211__add_workers_during_condor(rc: RestClient) -> None:
    """Add workers to workflow."""
    openapi_spec = await ewms_actions.query_for_schema(rc)

    workflow_id, task_id, tms_states = await ewms_actions.user_requests_new_workflow(
        rc,
        openapi_spec,
        list(CONDOR_LOCATIONS_LOOKUP.keys()),
    )

    # TMS STARTS TASKFORCES!
    tms_states = await ewms_actions.tms_starter(
        rc,
        openapi_spec,
        task_id,
        tms_states,
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "condor-submit",
        ("condor-submit", True),
    )

    # SEND UPDATES FROM TMS (JEL)!
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__1,
        COMPOUND_STATUSES__1,
    )
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__2,
        COMPOUND_STATUSES__2,
    )
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__3,
        COMPOUND_STATUSES__3,
    )
    # ADD MORE WORKERS!
    tms_states = await ewms_actions.add_more_workers(
        rc,
        openapi_spec,
        task_id,
        tms_states[0].shortname,  # add to this location
        tms_states,
    )
    _ = await ewms_actions.tms_starter(  # don't keep the return val -- its an incomplete list
        rc,
        openapi_spec,
        task_id,
        [  # include just the newbie, aka with n_taskforces=1
            StateForTMS(**{**asdict(tms_states[0]), **{"n_taskforces": 1}})
        ],
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "condor-submit",
        ("condor-submit", True),
    )

    # USER FINISHES WORKFLOW
    await ewms_actions.user_deactivates_workflow(
        rc,
        openapi_spec,
        "FINISHED",
        task_id,
        sum(s.n_taskforces for s in tms_states),
    )

    # CONDOR CLUSTERS FINISH UP!
    await ewms_actions.tms_condor_clusters_done(
        rc,
        openapi_spec,
        task_id,
        tms_states,
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "condor-complete",
        ("condor-complete", True),
    )

    # CHECK FINAL STATES...
    # NOTE: ^^^ already checked final taskforce states above
    # workflow:
    await check_workflow_deactivation(
        rc,
        openapi_spec,
        workflow_id,
        "FINISHED",
    )


async def test_220__add_workers_after_condor(rc: RestClient) -> None:
    """Add workers to workflow."""
    openapi_spec = await ewms_actions.query_for_schema(rc)

    workflow_id, task_id, tms_states = await ewms_actions.user_requests_new_workflow(
        rc,
        openapi_spec,
        list(CONDOR_LOCATIONS_LOOKUP.keys()),
    )

    # TMS STARTS TASKFORCES!
    tms_states = await ewms_actions.tms_starter(
        rc,
        openapi_spec,
        task_id,
        tms_states,
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "condor-submit",
        ("condor-submit", True),
    )

    # SEND UPDATES FROM TMS (JEL)!
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__1,
        COMPOUND_STATUSES__1,
    )
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__2,
        COMPOUND_STATUSES__2,
    )
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        tms_states,
        TOP_TASK_ERRORS__3,
        COMPOUND_STATUSES__3,
    )

    # USER FINISHES WORKFLOW
    await ewms_actions.user_deactivates_workflow(
        rc,
        openapi_spec,
        "FINISHED",
        task_id,
        sum(s.n_taskforces for s in tms_states),
    )

    # CONDOR CLUSTERS FINISH UP!
    await ewms_actions.tms_condor_clusters_done(
        rc,
        openapi_spec,
        task_id,
        tms_states,
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "condor-complete",
        ("condor-complete", True),
    )

    # ADD MORE WORKERS!
    with pytest.raises(
        requests.exceptions.HTTPError,
        match=re.escape(
            f"422 Client Error: cannot add a taskforce to a deactivated workflow "
            f"({workflow_id}) for url: http://localhost:8080/v1/task-directives/{task_id}/actions/add-workers"
        ),
    ):
        await ewms_actions.add_more_workers(
            rc,
            openapi_spec,
            task_id,
            tms_states[0].shortname,  # add to this location
            tms_states,
        )

    # re-check that nothing inadvertently changed
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        sum(s.n_taskforces for s in tms_states),
        "condor-complete",
        ("condor-complete", True),
    )

    # CHECK FINAL STATES...
    # NOTE: ^^^ already checked final taskforce states above
    # workflow:
    await check_workflow_deactivation(
        rc,
        openapi_spec,
        workflow_id,
        "FINISHED",
    )
