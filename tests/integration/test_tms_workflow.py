"""Mimic a TMS workflow, hitting the expected REST endpoints."""


import logging

import ewms_actions
from rest_tools.client import RestClient
from utils import request_and_validate

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


# ----------------------------------------------------------------------------


async def test_000(rc: RestClient) -> None:
    """Regular workflow."""
    openapi_spec = ewms_actions.query_for_schema(rc)

    task_id = ewms_actions.user_requests_new_task(
        rc,
        openapi_spec,
        list(CONDOR_LOCATIONS.keys()),
    )

    # TMS STARTS TASKFORCES!
    condor_locs_w_jel = ewms_actions.tms_starter(
        rc,
        openapi_spec,
        task_id,
        CONDOR_LOCATIONS,
    )

    # SEND UPDATES FROM TMS (JEL)!
    ewms_actions.tms_watcher_sends_report_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__1,
        COMPOUND_STATUSES__1,
    )
    ewms_actions.tms_watcher_sends_report_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__2,
        COMPOUND_STATUSES__2,
    )
    ewms_actions.tms_watcher_sends_report_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__3,
        COMPOUND_STATUSES__3,
    )

    # CONDOR CLUSTERS FINISH UP!
    ewms_actions.tms_condor_clusters_done(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
    )

    # CHECK FINAL STATES...
    resp = request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/tms/taskforces/find",
        {
            "query": {"task_id": task_id},
            "projection": ["tms_most_recent_action", "condor_complete_ts"],
        },
    )
    # fmt: off
    assert [tf["tms_most_recent_action"] for tf in resp["taskforces"]] == ["condor-submit"] * len(CONDOR_LOCATIONS)
    assert all(tf["condor_complete_ts"] for tf in resp["taskforces"])
    # fmt: on
    resp = request_and_validate(
        rc,
        openapi_spec,
        "GET",
        f"/task/directive/{task_id}",
    )
    assert resp["aborted"] is False


# ----------------------------------------------------------------------------


async def test_100__aborted_before_condor(rc: RestClient) -> None:
    """Aborted workflow."""
    openapi_spec = ewms_actions.query_for_schema(rc)

    task_id = ewms_actions.user_requests_new_task(
        rc,
        openapi_spec,
        list(CONDOR_LOCATIONS.keys()),
    )

    # ABORT!
    ewms_actions.user_aborts_task(
        rc,
        openapi_spec,
        task_id,
        CONDOR_LOCATIONS,
    )
    resp = request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/tms/taskforces/find",
        {"query": {"task_id": task_id}, "projection": ["tms_most_recent_action"]},
    )
    # fmt: off
    assert [tf["tms_most_recent_action"] for tf in resp["taskforces"]] == ["pending-stop"] * len(CONDOR_LOCATIONS)
    # fmt: on
    for loc in CONDOR_LOCATIONS.values():
        # check that there is NOTHING to start
        assert not request_and_validate(
            rc,
            openapi_spec,
            "GET",
            "/tms/taskforce/pending",
            {"collector": loc["collector"], "schedd": loc["schedd"]},
        )
    ewms_actions.tms_stopper(
        rc,
        openapi_spec,
        task_id,
        CONDOR_LOCATIONS,
    )
    for loc in CONDOR_LOCATIONS.values():
        # check that there is NOTHING to start
        assert not request_and_validate(
            rc,
            openapi_spec,
            "GET",
            "/tms/taskforce/pending",
            {"collector": loc["collector"], "schedd": loc["schedd"]},
        )

    # NOTE - since the taskforce(s) aren't started, there are no updates from a JEL

    # condor_locs_w_jel = ewms_actions.tms_starter(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     CONDOR_LOCATIONS,
    # )

    # # SEND UPDATES FROM TMS (JEL)!
    # ewms_actions.tms_watcher_sends_report_update(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     condor_locs_w_jel,
    #     TOP_TASK_ERRORS__1,
    #     COMPOUND_STATUSES__1,
    # )
    # ewms_actions.tms_watcher_sends_report_update(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     condor_locs_w_jel,
    #     TOP_TASK_ERRORS__2,
    #     COMPOUND_STATUSES__2,
    # )
    # ewms_actions.tms_watcher_sends_report_update(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     condor_locs_w_jel,
    #     TOP_TASK_ERRORS__3,
    #     COMPOUND_STATUSES__3,
    # )

    # ewms_actions.tms_condor_clusters_done(
    #     rc,
    #     openapi_spec,
    #     task_id,
    #     condor_locs_w_jel,
    # )

    # CHECK FINAL STATES...
    resp = request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/tms/taskforces/find",
        {
            "query": {"task_id": task_id},
            "projection": ["tms_most_recent_action", "condor_complete_ts"],
        },
    )
    # fmt: off
    assert [tf["tms_most_recent_action"] for tf in resp["taskforces"]] == ["condor-rm"] * len(CONDOR_LOCATIONS)
    assert all(tf["condor_complete_ts"] is None for tf in resp["taskforces"])
    # fmt: on


async def test_110__aborted_during_condor(rc: RestClient) -> None:
    """Aborted workflow."""
    openapi_spec = ewms_actions.query_for_schema(rc)

    task_id = ewms_actions.user_requests_new_task(
        rc,
        openapi_spec,
        list(CONDOR_LOCATIONS.keys()),
    )

    # TMS STARTS TASKFORCES!
    condor_locs_w_jel = ewms_actions.tms_starter(
        rc,
        openapi_spec,
        task_id,
        CONDOR_LOCATIONS,
    )

    # SEND UPDATES FROM TMS (JEL)!
    ewms_actions.tms_watcher_sends_report_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__1,
        COMPOUND_STATUSES__1,
    )

    # ABORT!
    ewms_actions.user_aborts_task(
        rc,
        openapi_spec,
        task_id,
        CONDOR_LOCATIONS,
    )
    resp = request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/tms/taskforces/find",
        {"query": {"task_id": task_id}, "projection": ["tms_most_recent_action"]},
    )
    # fmt: off
    assert [tf["tms_most_recent_action"] for tf in resp["taskforces"]] == ["pending-stop"] * len(CONDOR_LOCATIONS)
    # fmt: on
    ewms_actions.tms_stopper(
        rc,
        openapi_spec,
        task_id,
        CONDOR_LOCATIONS,
    )

    # continue, SEND UPDATES FROM TMS (JEL)
    ewms_actions.tms_watcher_sends_report_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__2,
        COMPOUND_STATUSES__2,
        aborted_during_condor=True,
    )
    ewms_actions.tms_watcher_sends_report_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__3,
        COMPOUND_STATUSES__3,
        aborted_during_condor=True,
    )

    # CONDOR CLUSTERS FINISH UP!
    ewms_actions.tms_condor_clusters_done(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
    )

    # CHECK FINAL STATES...
    resp = request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/tms/taskforces/find",
        {
            "query": {"task_id": task_id},
            "projection": ["tms_most_recent_action", "condor_complete_ts"],
        },
    )
    # fmt: off
    assert [tf["tms_most_recent_action"] for tf in resp["taskforces"]] == ["condor-rm"] * len(CONDOR_LOCATIONS)
    assert all(tf["condor_complete_ts"] for tf in resp["taskforces"])
    # fmt: on


async def test_111__aborted_during_condor(rc: RestClient) -> None:
    """Aborted workflow."""
    openapi_spec = ewms_actions.query_for_schema(rc)

    task_id = ewms_actions.user_requests_new_task(
        rc,
        openapi_spec,
        list(CONDOR_LOCATIONS.keys()),
    )

    # TMS STARTS TASKFORCES!
    condor_locs_w_jel = ewms_actions.tms_starter(
        rc,
        openapi_spec,
        task_id,
        CONDOR_LOCATIONS,
    )

    # SEND UPDATES FROM TMS (JEL)!
    ewms_actions.tms_watcher_sends_report_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__1,
        COMPOUND_STATUSES__1,
    )
    ewms_actions.tms_watcher_sends_report_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__2,
        COMPOUND_STATUSES__2,
    )
    ewms_actions.tms_watcher_sends_report_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__3,
        COMPOUND_STATUSES__3,
    )

    # ABORT!
    ewms_actions.user_aborts_task(
        rc,
        openapi_spec,
        task_id,
        CONDOR_LOCATIONS,
    )
    resp = request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/tms/taskforces/find",
        {"query": {"task_id": task_id}, "projection": ["tms_most_recent_action"]},
    )
    # fmt: off
    assert [tf["tms_most_recent_action"] for tf in resp["taskforces"]] == ["pending-stop"] * len(CONDOR_LOCATIONS)
    # fmt: on
    ewms_actions.tms_stopper(
        rc,
        openapi_spec,
        task_id,
        CONDOR_LOCATIONS,
    )

    # CONDOR CLUSTERS FINISH UP!
    ewms_actions.tms_condor_clusters_done(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
    )

    # CHECK FINAL STATES...
    resp = request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/tms/taskforces/find",
        {
            "query": {"task_id": task_id},
            "projection": ["tms_most_recent_action", "condor_complete_ts"],
        },
    )
    # fmt: off
    assert [tf["tms_most_recent_action"] for tf in resp["taskforces"]] == ["condor-rm"] * len(CONDOR_LOCATIONS)
    assert all(tf["condor_complete_ts"] for tf in resp["taskforces"])
    # fmt: on


async def test_120__aborted_after_condor(rc: RestClient) -> None:
    """Aborted workflow."""
    openapi_spec = ewms_actions.query_for_schema(rc)

    task_id = ewms_actions.user_requests_new_task(
        rc,
        openapi_spec,
        list(CONDOR_LOCATIONS.keys()),
    )

    # TMS STARTS TASKFORCES!
    condor_locs_w_jel = ewms_actions.tms_starter(
        rc,
        openapi_spec,
        task_id,
        CONDOR_LOCATIONS,
    )

    # SEND UPDATES FROM TMS (JEL)!
    ewms_actions.tms_watcher_sends_report_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__1,
        COMPOUND_STATUSES__1,
    )
    ewms_actions.tms_watcher_sends_report_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__2,
        COMPOUND_STATUSES__2,
    )
    ewms_actions.tms_watcher_sends_report_update(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
        TOP_TASK_ERRORS__3,
        COMPOUND_STATUSES__3,
    )

    # CONDOR CLUSTERS FINISH UP!
    ewms_actions.tms_condor_clusters_done(
        rc,
        openapi_spec,
        task_id,
        condor_locs_w_jel,
    )
    resp = request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/tms/taskforces/find",
        {"query": {"task_id": task_id}, "projection": ["tms_most_recent_action"]},
    )
    # fmt: off
    assert [tf["tms_most_recent_action"] for tf in resp["taskforces"]] == ["condor-submit"] * len(CONDOR_LOCATIONS)
    # fmt: on

    # ABORT!
    ewms_actions.user_aborts_task(
        rc,
        openapi_spec,
        task_id,
        CONDOR_LOCATIONS,
        aborted_after_condor=True,
    )
    resp = request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/tms/taskforces/find",
        {"query": {"task_id": task_id}, "projection": ["tms_most_recent_action"]},
    )
    # fmt: off
    assert [tf["tms_most_recent_action"] for tf in resp["taskforces"]] == ["condor-submit"] * len(CONDOR_LOCATIONS)
    # fmt: on
    for loc in CONDOR_LOCATIONS.values():
        # make sure there is NOTHING to stop (taskforces are 'condor-submit' not 'pending-stop')
        taskforce = request_and_validate(
            rc,
            openapi_spec,
            "GET",
            "/tms/taskforce/stop",
            {"collector": loc["collector"], "schedd": loc["schedd"]},
        )
        assert not taskforce

    # CHECK FINAL STATES...
    resp = request_and_validate(
        rc,
        openapi_spec,
        "POST",
        "/tms/taskforces/find",
        {
            "query": {"task_id": task_id},
            "projection": ["tms_most_recent_action", "condor_complete_ts"],
        },
    )
    # fmt: off
    assert [tf["tms_most_recent_action"] for tf in resp["taskforces"]] == ["condor-submit"] * len(CONDOR_LOCATIONS)
    assert all(tf["condor_complete_ts"] for tf in resp["taskforces"])
    # fmt: on
