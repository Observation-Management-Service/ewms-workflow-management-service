"""Mimic a TMS workflow, hitting the expected REST endpoints."""

import logging

import pytest
from rest_tools.client import RestClient

import ewms_actions
from utils import (
    _request_and_validate_and_print,
    check_nothing_to_start,
    check_nothing_to_stop,
    check_taskforce_states,
    check_workflow_deactivation,
)

LOGGER = logging.getLogger(__name__)

ROUTE_VERSION_PREFIX = "v0"

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

    workflow_id, task_id = await ewms_actions.user_requests_new_workflow(
        rc,
        openapi_spec,
        CONDOR_LOCATIONS,
    )

    # TMS STARTS TASKFORCES!
    condor_locs_w_jel = await ewms_actions.tms_starter(
        rc,
        openapi_spec,
        task_id,
        CONDOR_LOCATIONS,
    )

    # SEND UPDATES FROM TMS (JEL)!
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__1,
        COMPOUND_STATUSES__1,
    )
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__2,
        COMPOUND_STATUSES__2,
    )
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__3,
        COMPOUND_STATUSES__3,
    )

    # CONDOR CLUSTERS FINISH UP!
    await ewms_actions.tms_condor_clusters_done(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
    )

    # CHECK FINAL STATES...
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        len(CONDOR_LOCATIONS),
        "condor-complete",
        ("condor-complete", True),
    )
    await check_workflow_deactivation(
        rc,
        openapi_spec,
        workflow_id,
        None,
    )


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

    workflow_id, task_id = await ewms_actions.user_requests_new_workflow(
        rc,
        openapi_spec,
        CONDOR_LOCATIONS,
    )

    # DEACTIVATE!
    await ewms_actions.user_deactivates_workflow(
        rc,
        openapi_spec,
        kind_of_deactivation,
        task_id,
        CONDOR_LOCATIONS,
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        len(CONDOR_LOCATIONS),
        "pending-stopper",
        ("pending-stopper", True),
    )
    await check_nothing_to_start(rc, openapi_spec, CONDOR_LOCATIONS)
    await check_nothing_to_stop(rc, openapi_spec, CONDOR_LOCATIONS)
    await check_nothing_to_start(rc, openapi_spec, CONDOR_LOCATIONS)

    # NOTE - since the taskforce(s) aren't started, there are no updates from a JEL

    # condor_locs_w_jel = await ewms_actions.tms_starter(
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
    #     condor_locs_w_jel,
    #     TOP_TASK_ERRORS__1,
    #     COMPOUND_STATUSES__1,
    # )
    # await ewms_actions.tms_watcher_sends_status_update(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     condor_locs_w_jel,
    #     TOP_TASK_ERRORS__2,
    #     COMPOUND_STATUSES__2,
    # )
    # await ewms_actions.tms_watcher_sends_status_update(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     condor_locs_w_jel,
    #     TOP_TASK_ERRORS__3,
    #     COMPOUND_STATUSES__3,
    # )

    # await ewms_actions.tms_condor_clusters_done(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     condor_locs_w_jel,
    # )

    # CHECK FINAL STATES...
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        len(CONDOR_LOCATIONS),
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

    workflow_id, task_id = await ewms_actions.user_requests_new_workflow(
        rc,
        openapi_spec,
        CONDOR_LOCATIONS,
    )

    # DEACTIVATE!
    await ewms_actions.user_deactivates_workflow(
        rc,
        openapi_spec,
        kind_of_deactivation,
        task_id,
        CONDOR_LOCATIONS,
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        len(CONDOR_LOCATIONS),
        "pending-stopper",
        ("pending-stopper", True),
    )
    await check_nothing_to_start(rc, openapi_spec, CONDOR_LOCATIONS)
    await check_nothing_to_stop(rc, openapi_spec, CONDOR_LOCATIONS)
    await check_nothing_to_start(rc, openapi_spec, CONDOR_LOCATIONS)

    # await ewms_actions.taskforce_launch_control_marks_taskforces_pending_starter(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     len(CONDOR_LOCATIONS),
    # )

    # NOTE - since the taskforce(s) aren't started, there are no updates from a JEL

    # condor_locs_w_jel = await ewms_actions.tms_starter(
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
    #     condor_locs_w_jel,
    #     TOP_TASK_ERRORS__1,
    #     COMPOUND_STATUSES__1,
    # )
    # await ewms_actions.tms_watcher_sends_status_update(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     condor_locs_w_jel,
    #     TOP_TASK_ERRORS__2,
    #     COMPOUND_STATUSES__2,
    # )
    # await ewms_actions.tms_watcher_sends_status_update(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     condor_locs_w_jel,
    #     TOP_TASK_ERRORS__3,
    #     COMPOUND_STATUSES__3,
    # )

    # await ewms_actions.tms_condor_clusters_done(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     condor_locs_w_jel,
    # )

    # CHECK FINAL STATES...
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        len(CONDOR_LOCATIONS),
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

    workflow_id, task_id = await ewms_actions.user_requests_new_workflow(
        rc,
        openapi_spec,
        CONDOR_LOCATIONS,
    )

    # TMS STARTS TASKFORCES!
    condor_locs_w_jel = await ewms_actions.tms_starter(
        rc,
        openapi_spec,
        task_id,
        CONDOR_LOCATIONS,
    )

    # SEND UPDATES FROM TMS (JEL)!
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__1,
        COMPOUND_STATUSES__1,
    )

    # DEACTIVATE!
    await ewms_actions.user_deactivates_workflow(
        rc,
        openapi_spec,
        kind_of_deactivation,
        task_id,
        CONDOR_LOCATIONS,
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        len(CONDOR_LOCATIONS),
        "pending-stopper",
        ("pending-stopper", True),
    )
    await ewms_actions.tms_stopper(
        rc,
        openapi_spec,
        task_id,
        CONDOR_LOCATIONS,
    )

    # continue, SEND UPDATES FROM TMS (JEL)
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__2,
        COMPOUND_STATUSES__2,
    )
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__3,
        COMPOUND_STATUSES__3,
    )

    # CONDOR CLUSTERS FINISH UP!
    await ewms_actions.tms_condor_clusters_done(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
    )

    # CHECK FINAL STATES...
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        len(CONDOR_LOCATIONS),
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

    workflow_id, task_id = await ewms_actions.user_requests_new_workflow(
        rc,
        openapi_spec,
        CONDOR_LOCATIONS,
    )

    # TMS STARTS TASKFORCES!
    condor_locs_w_jel = await ewms_actions.tms_starter(
        rc,
        openapi_spec,
        task_id,
        CONDOR_LOCATIONS,
    )

    # SEND UPDATES FROM TMS (JEL)!
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__1,
        COMPOUND_STATUSES__1,
    )
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__2,
        COMPOUND_STATUSES__2,
    )
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__3,
        COMPOUND_STATUSES__3,
    )

    # DEACTIVATE!
    await ewms_actions.user_deactivates_workflow(
        rc,
        openapi_spec,
        kind_of_deactivation,
        task_id,
        CONDOR_LOCATIONS,
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        len(CONDOR_LOCATIONS),
        "pending-stopper",
        ("pending-stopper", True),
    )
    await ewms_actions.tms_stopper(
        rc,
        openapi_spec,
        task_id,
        CONDOR_LOCATIONS,
    )

    # CONDOR CLUSTERS FINISH UP!
    await ewms_actions.tms_condor_clusters_done(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
    )

    # CHECK FINAL STATES...
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        len(CONDOR_LOCATIONS),
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

    workflow_id, task_id = await ewms_actions.user_requests_new_workflow(
        rc,
        openapi_spec,
        CONDOR_LOCATIONS,
    )

    # TMS STARTS TASKFORCES!
    condor_locs_w_jel = await ewms_actions.tms_starter(
        rc,
        openapi_spec,
        task_id,
        CONDOR_LOCATIONS,
    )

    # SEND UPDATES FROM TMS (JEL)!
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__1,
        COMPOUND_STATUSES__1,
    )
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__2,
        COMPOUND_STATUSES__2,
    )
    await ewms_actions.tms_watcher_sends_status_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__3,
        COMPOUND_STATUSES__3,
    )

    # CONDOR CLUSTERS FINISH UP!
    await ewms_actions.tms_condor_clusters_done(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        len(CONDOR_LOCATIONS),
        "condor-complete",
        ("condor-complete", True),
    )

    # DEACTIVATE!
    await ewms_actions.user_deactivates_workflow(
        rc,
        openapi_spec,
        kind_of_deactivation,
        task_id,
        CONDOR_LOCATIONS,
        deactivated_after_condor_stopped=True,
    )
    await check_taskforce_states(
        rc,
        openapi_spec,
        task_id,
        len(CONDOR_LOCATIONS),
        "condor-complete",
        ("pending-stopper", False),
    )
    for loc in CONDOR_LOCATIONS.values():
        # make sure there is NOTHING to stop (taskforces are not 'pending-stopper')
        taskforce = await _request_and_validate_and_print(
            rc,
            openapi_spec,
            "GET",
            f"/{ROUTE_VERSION_PREFIX}/tms/pending-stopper/taskforces",
            {"collector": loc["collector"], "schedd": loc["schedd"]},
        )
        assert not taskforce

    # CHECK FINAL STATES...
    # NOTE: ^^^ already checked final taskforce states above
    # workflow:
    await check_workflow_deactivation(
        rc,
        openapi_spec,
        workflow_id,
        kind_of_deactivation,
    )
