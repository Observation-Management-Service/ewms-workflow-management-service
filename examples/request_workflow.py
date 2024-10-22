"""A simple example script (single-task workflow) to send to EWMS."""

import argparse
import asyncio
import itertools
import json
import logging
import random
import threading
import time
from pathlib import Path
from typing import Any, TYPE_CHECKING

import wipac_dev_tools.logging_tools

if TYPE_CHECKING:  # not installing dependency just for example script
    Queue = Any
else:
    from mqclient import Queue

from rest_tools.client import RestClient, SavedDeviceGrantAuth

LOGGER = logging.getLogger(__name__)


BUNCH_OF_WORDS = set(
    [
        "foo",
        "bar",
        "baz",
        "dummy",
        "test",
        "data",
        "example",
        "abc",
        "xyz",
        "apple",
        "banana",
        "grapefruit",
        "grape",
        "pineapple",
        "watermelon",
        "kiwi",
        "pear",
        "strawberry",
        "melon",
        "carrot",
        "potato",
        "broccoli",
        "lettuce",
        "cucumber",
        "tomato",
        "onion",
        "garlic",
        "pepper",
        "spinach",
        "dog",
        "cat",
        "bird",
        "fish",
        "rabbit",
        "hamster",
        "turtle",
        "snake",
        "lizard",
        "frog",
        "red",
        "blue",
        "green",
        "yellow",
        "orange",
        "purple",
        "black",
        "white",
        "gray",
        "brown",
    ]
)


def generate_strings(n: int):
    return [f"{random.choice(list(BUNCH_OF_WORDS))}{i}" for i in range(n)]


async def load_queue(queue: Queue, n: int) -> list[str]:
    """Load the in-queue's with several contents."""
    LOGGER.info("Loading input events...")

    strings = generate_strings(n)

    async with queue.open_pub() as pub:
        for i, msg in enumerate(strings):
            await pub.send(msg)
            LOGGER.debug(f"enqueued #{i}: {msg}")

    return strings


async def request_workflow(
    rc: RestClient,
    pilot_cvmfs_image_tag: str,
    n_workers: int,
) -> tuple[str, str, str]:
    """Request EWMS (WMS) to process a single-task workflow."""
    LOGGER.info("Requesting single-task workflow to EWMS...")

    post_body = {
        "public_queue_aliases": ["input-queue", "output-queue"],
        "tasks": [
            {
                "cluster_locations": ["sub-2"],
                "input_queue_aliases": ["input-queue"],
                "output_queue_aliases": ["output-queue"],
                "task_image": "/cvmfs/icecube.opensciencegrid.org/containers/ewms/observation-management-service/ewms-task-management-service:0.1.44",
                "task_args": "cp {{INFILE}} {{OUTFILE}}",
                "n_workers": n_workers,
                "worker_config": {
                    "do_transfer_worker_stdouterr": True,
                    "max_worker_runtime": 60 * 10,
                    "n_cores": 1,
                    "priority": 99,
                    "worker_disk": "512M",
                    "worker_memory": "512M",
                },
                # optionally add this...
                **(
                    {
                        "pilot_config": {
                            "environment": {},
                            "input_files": [],
                            "image": pilot_cvmfs_image_tag,
                        }
                    }
                    if pilot_cvmfs_image_tag
                    else {}
                ),
            }
        ],
    }
    resp = await rc.request("POST", "/v0/workflows", post_body)

    LOGGER.debug(json.dumps(resp))

    return (
        resp["workflow"]["workflow_id"],
        resp["task_directives"][0]["input_queues"][0],
        resp["task_directives"][0]["output_queues"][0],
    )


async def read_queue(queue: Queue, output_events: list[str]) -> None:
    """Read and dump the out-queue's contents."""
    LOGGER.info("Reading output events...")

    # using a set b/c...
    # 1. mqclient doesn't guarantee deliver-once delivery
    # 2. we know that result values are unique (we have domain knowledge for this)
    got: set[Any] = set()
    # alternatively, we could adjust the timeout, but that requires other assumptions

    async with queue.open_sub() as sub:
        i = 0
        async for msg in sub:
            LOGGER.debug(f"received #{i}: {msg}")
            got.add(msg)
            i += 1
            if sorted(got) == sorted(output_events):
                break

    LOGGER.info("Done reading queue -- received all output events")


async def monitor_workflow(rc: RestClient, workflow_id: str) -> None:
    """Routinely query WMS."""
    LOGGER.info("Monitoring WMS...")

    prev_workflow = {}  # type: ignore
    prev_task_directives = []  # type: ignore
    prev_taskforces = []  # type: ignore

    for i in itertools.count():
        if i > 0:
            time.sleep(15)  # in thread, so ok

        workflow = await rc.request(
            "GET",
            f"/v0/workflows/{workflow_id}",
        )
        task_directives = (
            await rc.request(
                "POST",
                "/v0/query/task-directives",
                {"query": {"workflow_id": workflow_id}},
            )
        )["task_directives"]

        if i == 0:
            taskforces = (
                await rc.request(
                    "POST",
                    "/v0/query/taskforces",
                    {"query": {"workflow_id": workflow_id}},
                )
            )["taskforces"]
        else:
            taskforces = (
                await rc.request(
                    "POST",
                    "/v0/query/taskforces",
                    {
                        "query": {"workflow_id": workflow_id},
                        "projection": [
                            "phase",
                            "phase_change_log",
                            "compound_statuses",
                            "top_task_errors",
                            "taskforce_uuid",
                            "task_id",
                        ],
                    },
                )
            )["taskforces"]

        if (prev_workflow, prev_task_directives, prev_taskforces) == (
            workflow,
            task_directives,
            taskforces,
        ):
            LOGGER.info("no change")
            continue
        prev_workflow, prev_task_directives, prev_taskforces = (
            workflow,
            task_directives,
            taskforces,
        )

        LOGGER.info("WORKFLOW:")
        LOGGER.info(json.dumps(workflow, indent=4))
        LOGGER.info("TASK DIRECTIVE(S):")
        LOGGER.info(json.dumps(task_directives, indent=4))
        LOGGER.info("TASKFORCES:")
        LOGGER.info(json.dumps(taskforces, indent=4))

        LOGGER.info("\n\n\n\n\n\n")
        LOGGER.info("Looking again in 15 seconds...")


async def main() -> None:
    """explain."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--n-input-events",
        required=True,
        type=int,
        help="the number of input events to put into EWMS",
    )
    parser.add_argument(
        "--pilot-cvmfs-image-tag",
        default="",
        help="the tag (version) of the pilot example image that the workers will use. Ex: 0.1.11",
    )
    parser.add_argument(
        "--n-workers",
        default=5,
        type=int,
        help="the number of workers to use",
    )
    parser.add_argument(
        "--monitor-workflow-id",
        default="",
        help="the workflow id to resume monitoring instead of requesting a new workflow",
    )
    args = parser.parse_args()
    wipac_dev_tools.logging_tools.log_argparse_args(args)

    rc = SavedDeviceGrantAuth(
        "https://ewms-dev.icecube.aq",
        token_url="https://keycloak.icecube.wisc.edu/auth/realms/IceCube",
        filename=str(Path("~/device-refresh-token").expanduser().resolve()),
        client_id="ewms-dev-public",
        retries=0,
    )

    # do we just want to resume monitoring?
    if args.monitor_workflow_id:
        return await monitor_workflow(rc, args.monitor_workflow_id)

    # request workflow
    workflow_id, input_queue, output_queue = await request_workflow(
        rc,
        args.pilot_cvmfs_image_tag,
        args.n_workers,
    )

    # monitor
    def monitor_sync_wrapper(rc: RestClient, workflow_id: str) -> None:
        asyncio.run(monitor_workflow(rc, workflow_id))

    threading.Thread(
        target=monitor_sync_wrapper,
        args=(rc, workflow_id),
        daemon=True,
    ).start()

    # wait until queues are activated
    LOGGER.info("getting queues...")
    mqprofiles: list[dict] = []
    while not (mqprofiles and all(m["is_activated"] for m in mqprofiles)):
        await asyncio.sleep(10)
        mqprofiles = (
            await rc.request(
                "GET",
                f"/v0/mqs/workflows/{workflow_id}/mq-profiles/public",
            )
        )["mqprofiles"]
    LOGGER.info(f"{mqprofiles=}")

    # load & read queues
    input_mqprofile = next(p for p in mqprofiles if p["mqid"] == input_queue)
    input_events = await load_queue(
        queue=Queue(
            input_mqprofile["broker_type"],
            address=input_mqprofile["broker_address"],
            name=input_mqprofile["mqid"],
            auth_token=input_mqprofile["auth_token"],
        ),
        n=args.n_input_events,
    )
    output_mqprofile = next(p for p in mqprofiles if p["mqid"] == output_queue)
    await read_queue(
        queue=Queue(
            output_mqprofile["broker_type"],
            address=output_mqprofile["broker_address"],
            name=output_mqprofile["mqid"],
            auth_token=output_mqprofile["auth_token"],
            timeout=60 * 20,
        ),
        output_events=input_events,  # NOTE: this is dependent on the task image!
    )

    # wait at end, so monitor thread can get some final updates
    await asyncio.sleep(60)


if __name__ == "__main__":
    hand = logging.StreamHandler()
    hand.setFormatter(
        logging.Formatter(
            "%(asctime)s.%(msecs)03d [%(levelname)8s] %(name)s[%(process)d] %(message)s <%(filename)s:%(lineno)s/%(funcName)s()>",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logging.getLogger().addHandler(hand)
    wipac_dev_tools.logging_tools.set_level(
        "DEBUG",
        first_party_loggers=LOGGER,
        third_party_level="WARNING",
        future_third_parties=["OpenIDRestClient"],
        specialty_loggers={"mqclient": "INFO"},
    )
    asyncio.run(main())
