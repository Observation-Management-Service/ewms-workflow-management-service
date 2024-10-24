"""Test the MQS scheduling logic with the workflow_mq_activator module/daemon.

Runs everything in main process and thread. Uses a real mongo database
and mock/patched MQS REST calls."""

import asyncio
import itertools
import logging
import time
from typing import Any, AsyncIterator, Iterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from wms import config, database, schema, workflow_mq_activator

logging.getLogger("pymongo").setLevel(logging.INFO)

TEST_WORKFLOWS = [
    {
        "workflow_id": workflow_id,
        "timestamp": 1 + i,
        "priority": 10,
        "mq_activated_ts": None,
        "_mq_activation_retry_at_ts": config.MQS_RETRY_AT_TS_DEFAULT_VALUE,
        "aborted": False,
    }
    for i, workflow_id in enumerate(
        # NOTE: naming format matters for _make_test_task_directives()
        ["A1", "B2", "C3", "D4", "E5"]
    )
]


async def alist(async_iterator: AsyncIterator) -> list:
    return [x async for x in async_iterator]


def _make_test_task_directives(workflow: dict) -> Iterator[dict]:
    for n in range(int(workflow["workflow_id"][1])):
        yield {
            "task_id": f"td-{workflow['workflow_id']}-{n}",
            "workflow_id": workflow["workflow_id"],
            #
            "cluster_locations": ["foo", "bar"],
            "task_image": "bap",
            "task_args": "--baz bat",
            "timestamp": 1 + n,
            #
            "input_queues": [f"q-td-{n}"],
            "output_queues": [f"q-td-{n+1}"],  # n+1 to overlap (i.e. a chain of tasks)
        }


def _make_test_taskforce(task_directive: dict, location: str, i: int) -> dict:
    return {
        "taskforce_uuid": f"{task_directive['task_id']}-{i}",
        "task_id": task_directive["task_id"],
        "workflow_id": task_directive["workflow_id"],
        #
        "timestamp": task_directive["timestamp"],
        "collector": f"collector-{location}",
        "schedd": f"schedd-{location}",
        "n_workers": 100,
        "pilot_config": {
            "tag": "v1.2.3",
            "environment": {
                "EWMS_PILOT_TASK_IMAGE": task_directive["task_image"],
                "EWMS_PILOT_TASK_ARGS": task_directive["task_args"],
            },
            "input_files": [],
        },
        "worker_config": {
            "do_transfer_worker_stdouterr": True,
            "max_worker_runtime": 60 * 10,
            "n_cores": 1,
            "priority": 99,
            "worker_disk": "512M",
            "worker_memory": "512M",
        },
        "cluster_id": None,
        "submit_dict": {},
        "job_event_log_fpath": "",
        "phase": schema.enums.TaskforcePhase.PRE_MQ_ACTIVATOR.value,
        "phase_change_log": [
            {
                "target_phase": schema.enums.TaskforcePhase.PRE_MQ_ACTIVATOR.value,
                "timestamp": task_directive[
                    "timestamp"  # in real life, real value would be slightly greater
                ],
                "source_event_time": None,
                "was_successful": True,
                "source_entity": "User",
                "description": "During initial workflow creation.",
            }
        ],
        "compound_statuses": {},
        "top_task_errors": {},
    }


class MQSRESTCalls:
    call_ct = -1  # class var
    last_ts = 0.0
    retry_dues: dict[str, float] = {}

    @staticmethod
    def request_activation_to_mqs(_: Any, workflow: dict) -> dict:
        assert workflow

        diff = time.time() - MQSRESTCalls.last_ts
        MQSRESTCalls.last_ts = time.time()
        MQSRESTCalls.call_ct += 1

        match MQSRESTCalls.call_ct:
            # accept A
            case 0:
                assert workflow["workflow_id"] == "A1"
                # assert config.ENV.WORKFLOW_MQ_ACTIVATOR_DELAY <= diff <= config.ENV.WORKFLOW_MQ_ACTIVATOR_DELAY+1  # check won't work for first call
                return {
                    "mqprofiles": [
                        # make dummy objs from all queues for all task directives
                        {
                            "mqid": mqid,
                            "auth_token": f"DUMMY_TOKEN_{mqid}",
                            "broker_type": f"DUMMY_BROKER_TYPE_{mqid}",
                            "broker_address": f"DUMMY_BROKER_ADDRESS_{mqid}",
                        }
                        for mqid in set(
                            itertools.chain.from_iterable(
                                td["input_queues"] + td["output_queues"]
                                for td in _make_test_task_directives(workflow)
                            )
                        )
                    ]
                }
            # deny B
            case 1:
                assert workflow["workflow_id"] == "B2"
                assert (
                    config.ENV.WORKFLOW_MQ_ACTIVATOR_DELAY
                    <= diff
                    <= config.ENV.WORKFLOW_MQ_ACTIVATOR_DELAY + 1
                )
                MQSRESTCalls.retry_dues[workflow["workflow_id"]] = (
                    time.time() + config.ENV.WORKFLOW_MQ_ACTIVATOR_MQS_RETRY_WAIT
                )
                return {"try_again_later": True}
            # accept C
            case 2:
                assert workflow["workflow_id"] == "C3"
                assert (  # prev was denied AND this one was accepted, so this was a short sleep
                    config.TASK_MQ_ACTIVATOR_SHORTEST_SLEEP
                    <= diff
                    <= config.TASK_MQ_ACTIVATOR_SHORTEST_SLEEP + 1
                )
                return {
                    "mqprofiles": [
                        # make dummy objs from all queues for all task directives
                        {
                            "mqid": mqid,
                            "auth_token": f"DUMMY_TOKEN_{mqid}",
                            "broker_type": f"DUMMY_BROKER_TYPE_{mqid}",
                            "broker_address": f"DUMMY_BROKER_ADDRESS_{mqid}",
                        }
                        for mqid in set(
                            itertools.chain.from_iterable(
                                td["input_queues"] + td["output_queues"]
                                for td in _make_test_task_directives(workflow)
                            )
                        )
                    ]
                }
            # accept D
            case 3:
                assert workflow["workflow_id"] == "D4"
                assert (
                    config.ENV.WORKFLOW_MQ_ACTIVATOR_DELAY
                    <= diff
                    <= config.ENV.WORKFLOW_MQ_ACTIVATOR_DELAY + 1
                )
                return {
                    "mqprofiles": [
                        # make dummy objs from all queues for all task directives
                        {
                            "mqid": mqid,
                            "auth_token": f"DUMMY_TOKEN_{mqid}",
                            "broker_type": f"DUMMY_BROKER_TYPE_{mqid}",
                            "broker_address": f"DUMMY_BROKER_ADDRESS_{mqid}",
                        }
                        for mqid in set(
                            itertools.chain.from_iterable(
                                td["input_queues"] + td["output_queues"]
                                for td in _make_test_task_directives(workflow)
                            )
                        )
                    ]
                }
            # deny E
            case 4:
                assert workflow["workflow_id"] == "E5"
                assert (
                    config.ENV.WORKFLOW_MQ_ACTIVATOR_DELAY
                    <= diff
                    <= config.ENV.WORKFLOW_MQ_ACTIVATOR_DELAY + 1
                )
                MQSRESTCalls.retry_dues[workflow["workflow_id"]] = (
                    time.time() + config.ENV.WORKFLOW_MQ_ACTIVATOR_MQS_RETRY_WAIT
                )
                return {"try_again_later": True}
            # retry: re-deny B
            case 5:
                assert workflow["workflow_id"] == "B2"
                assert (
                    MQSRESTCalls.retry_dues[workflow["workflow_id"]]
                    <= time.time()
                    <= MQSRESTCalls.retry_dues[workflow["workflow_id"]] + 2.5
                )
                MQSRESTCalls.retry_dues[workflow["workflow_id"]] = (
                    time.time() + config.ENV.WORKFLOW_MQ_ACTIVATOR_MQS_RETRY_WAIT
                )
                return {"try_again_later": True}
            # retry: re-deny E
            case 6:
                assert workflow["workflow_id"] == "E5"
                assert (
                    MQSRESTCalls.retry_dues[workflow["workflow_id"]]
                    <= time.time()
                    <= MQSRESTCalls.retry_dues[workflow["workflow_id"]] + 2.5
                )
                MQSRESTCalls.retry_dues[workflow["workflow_id"]] = (
                    time.time() + config.ENV.WORKFLOW_MQ_ACTIVATOR_MQS_RETRY_WAIT
                )
                return {"try_again_later": True}
            # retry: re-deny B
            case 7:
                assert workflow["workflow_id"] == "B2"
                assert (
                    MQSRESTCalls.retry_dues[workflow["workflow_id"]]
                    <= time.time()
                    <= MQSRESTCalls.retry_dues[workflow["workflow_id"]] + 2.5
                )
                MQSRESTCalls.retry_dues[workflow["workflow_id"]] = (
                    time.time() + config.ENV.WORKFLOW_MQ_ACTIVATOR_MQS_RETRY_WAIT
                )
                return {"try_again_later": True}
            # retry: accept E
            case 8:
                assert workflow["workflow_id"] == "E5"
                assert (
                    MQSRESTCalls.retry_dues[workflow["workflow_id"]]
                    <= time.time()
                    <= MQSRESTCalls.retry_dues[workflow["workflow_id"]] + 2.5
                )
                return {
                    "mqprofiles": [
                        # make dummy objs from all queues for all task directives
                        {
                            "mqid": mqid,
                            "auth_token": f"DUMMY_TOKEN_{mqid}",
                            "broker_type": f"DUMMY_BROKER_TYPE_{mqid}",
                            "broker_address": f"DUMMY_BROKER_ADDRESS_{mqid}",
                        }
                        for mqid in set(
                            itertools.chain.from_iterable(
                                td["input_queues"] + td["output_queues"]
                                for td in _make_test_task_directives(workflow)
                            )
                        )
                    ]
                }
            # retry: re-deny B
            case 9:
                assert workflow["workflow_id"] == "B2"
                assert (
                    MQSRESTCalls.retry_dues[workflow["workflow_id"]]
                    <= time.time()
                    <= MQSRESTCalls.retry_dues[workflow["workflow_id"]] + 2.5
                )
                MQSRESTCalls.retry_dues[workflow["workflow_id"]] = (
                    time.time() + config.ENV.WORKFLOW_MQ_ACTIVATOR_MQS_RETRY_WAIT
                )
                return {"try_again_later": True}
            # retry: accept B
            case 10:
                assert workflow["workflow_id"] == "B2"
                assert (
                    MQSRESTCalls.retry_dues[workflow["workflow_id"]]
                    <= time.time()
                    <= MQSRESTCalls.retry_dues[workflow["workflow_id"]] + 2.5
                )
                return {
                    "mqprofiles": [
                        # make dummy objs from all queues for all task directives
                        {
                            "mqid": mqid,
                            "auth_token": f"DUMMY_TOKEN_{mqid}",
                            "broker_type": f"DUMMY_BROKER_TYPE_{mqid}",
                            "broker_address": f"DUMMY_BROKER_ADDRESS_{mqid}",
                        }
                        for mqid in set(
                            itertools.chain.from_iterable(
                                td["input_queues"] + td["output_queues"]
                                for td in _make_test_task_directives(workflow)
                            )
                        )
                    ]
                }
            # ???
            case other:
                print(other)
                assert 0


@patch("wms.workflow_mq_activator.request_activation_to_mqs", new_callable=AsyncMock)
@patch("wms.workflow_mq_activator.RestClient", new=MagicMock)  # it's a from-import
async def test_000(mock_req_act_to_mqs: AsyncMock) -> None:
    """Test the MQS scheduling with several tasks and requests."""
    mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")  # type: ignore[var-annotated]
    workflows_client = database.client.MongoValidatedCollection(
        mongo_client,
        database.utils.WORKFLOWS_COLL_NAME,
    )
    task_directives_client = database.client.MongoValidatedCollection(
        mongo_client,
        database.utils.TASK_DIRECTIVES_COLL_NAME,
    )
    taskforces_client = database.client.MongoValidatedCollection(
        mongo_client,
        database.utils.TASKFORCES_COLL_NAME,
    )

    # ingest data into mongo as if REST user did so
    for wf_db in TEST_WORKFLOWS:
        await workflows_client.insert_one(wf_db)
        for td in _make_test_task_directives(wf_db):
            await task_directives_client.insert_one(td)
            for i, location in enumerate(td["cluster_locations"]):  # type: ignore
                await taskforces_client.insert_one(
                    _make_test_taskforce(td, location, i)
                )

    # pre-patch all the REST calls to MQS
    mock_req_act_to_mqs.side_effect = MQSRESTCalls.request_activation_to_mqs

    #
    # STARTUP THE WORKFLOW MQ ACTIVATOR
    with pytest.raises(asyncio.TimeoutError):
        # use asyncio's timeout to artificially stop loop, otherwise it'd go forever
        await asyncio.wait_for(workflow_mq_activator.run(mongo_client), timeout=60)

    #
    #
    # at this point in time, the mq activator will have completed all work to be done
    #
    #

    # check mongo db state
    assert len(await alist(workflows_client.find_all({}, []))) == len(TEST_WORKFLOWS)
    # look at workflows, individually
    async for wf_db in workflows_client.find_all({}, []):
        exp = next(  # using 'next' gives shorter debug than w/ 'in'
            w for w in TEST_WORKFLOWS if w["workflow_id"] == wf_db["workflow_id"]
        )
        # ignore the mq keys -- functionality is tested by MQSRESTCalls.request_activation_to_mqs
        ignore = ["mq_activated_ts", "_mq_activation_retry_at_ts"]
        assert {k: v for k, v in wf_db.items() if k not in ignore} == {
            k: v for k, v in exp.items() if k not in ignore
        }
        # look at task_directives by workflow_id
        n_asserted = 0
        async for td_db in task_directives_client.find_all(
            {"workflow_id": wf_db["workflow_id"]}, []
        ):
            #
            # ASSEMBLE LIST OF EXPECTED TASKFORCES
            expected_tfs = []  # type: ignore
            for i, location in enumerate(td_db["cluster_locations"]):  # 1 tf per loc
                tf = _make_test_taskforce(td_db, location, i)
                # update fields that the mq activator should've also done
                tf["phase"] = str(schema.enums.TaskforcePhase.PRE_LAUNCH)
                tf["phase_change_log"] = [
                    {
                        "target_phase": schema.enums.TaskforcePhase.PRE_MQ_ACTIVATOR.value,
                        "timestamp": td_db[
                            "timestamp"  # in real life, real value would be slightly greater
                        ],
                        "source_event_time": None,
                        "was_successful": True,
                        "source_entity": "User",
                        "description": "During initial workflow creation.",
                    },
                    {
                        "description": "",
                        "source_entity": "Workflow MQ Activator",
                        "source_event_time": None,
                        "target_phase": schema.enums.TaskforcePhase.PRE_LAUNCH.value,
                        "timestamp": 1729625971.0202708,
                        "was_successful": True,
                    },
                ]
                tf["pilot_config"]["environment"] = {
                    # input
                    "EWMS_PILOT_QUEUE_INCOMING": td_db["input_queues"],
                    "EWMS_PILOT_QUEUE_INCOMING_AUTH_TOKEN": [
                        f"DUMMY_TOKEN_{q}" for q in td_db["input_queues"]
                    ],
                    "EWMS_PILOT_QUEUE_INCOMING_BROKER_TYPE": [
                        f"DUMMY_BROKER_TYPE_{q}" for q in td_db["input_queues"]
                    ],
                    "EWMS_PILOT_QUEUE_INCOMING_BROKER_ADDRESS": [
                        f"DUMMY_BROKER_ADDRESS_{q}" for q in td_db["input_queues"]
                    ],
                    # output
                    "EWMS_PILOT_QUEUE_OUTGOING": td_db["output_queues"],
                    "EWMS_PILOT_QUEUE_OUTGOING_AUTH_TOKEN": [
                        f"DUMMY_TOKEN_{q}" for q in td_db["output_queues"]
                    ],
                    "EWMS_PILOT_QUEUE_OUTGOING_BROKER_TYPE": [
                        f"DUMMY_BROKER_TYPE_{q}" for q in td_db["output_queues"]
                    ],
                    "EWMS_PILOT_QUEUE_OUTGOING_BROKER_ADDRESS": [
                        f"DUMMY_BROKER_ADDRESS_{q}" for q in td_db["output_queues"]
                    ],
                    "EWMS_PILOT_TASK_IMAGE": td_db["task_image"],
                    "EWMS_PILOT_TASK_ARGS": td_db["task_args"],
                }
                expected_tfs.append(tf)
            #
            # get all taskforces for task_id
            actual_tfs = await alist(
                taskforces_client.find_all({"task_id": td_db["task_id"]}, [])
            )
            # first, skip the timestamps generated by the mq activator
            for tf in expected_tfs + actual_tfs:
                for pcl in tf["phase_change_log"]:  # should only be one entry
                    if pcl["target_phase"] == schema.enums.TaskforcePhase.PRE_LAUNCH:
                        pcl["timestamp"] = -1.0
            # now, compare
            assert actual_tfs == expected_tfs
            n_asserted += len(expected_tfs)
        #
        # sanity check by querying w/ workflow_id
        assert n_asserted == len(
            await alist(
                taskforces_client.find_all({"workflow_id": wf_db["workflow_id"]}, [])
            )
        )
