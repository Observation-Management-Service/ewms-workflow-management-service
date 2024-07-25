"""A simple example script (single-task workflow) to send to EWMS.

See https://github.com/Observation-Management-Service/ewms-pilot/blob/main/examples/do_task.py
"""

import argparse
import asyncio
import itertools
import json
import logging
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


MSGS = set(
    [
        "foo",
        "bar",
        "baz",
        "dummy",
        "test",
        "data",
        "example",
        "123",
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


async def load_queue(queue: Queue) -> None:
    """Load the in-queue's with several contents."""
    LOGGER.info("Loading in-queue with messages...")

    async with queue.open_pub() as pub:
        for i, msg in enumerate(MSGS):
            await pub.send(msg)
            LOGGER.debug(f"enqueued #{i}: {msg}")


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
                "task_image": f"/cvmfs/icecube.opensciencegrid.org/containers/ewms/observation-management-service/ewms-pilot:{pilot_cvmfs_image_tag}",
                "task_args": "python /app/examples/do_task.py",
                "environment": {},
                "n_workers": n_workers,
                "worker_config": {
                    "do_transfer_worker_stdouterr": True,
                    "max_worker_runtime": 60 * 10,
                    "n_cores": 1,
                    "priority": 99,
                    "worker_disk": "512M",
                    "worker_memory": "512M",
                },
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


async def read_queue(queue: Queue) -> None:
    """Read and dump the out-queue's contents."""
    LOGGER.info("Reading out-queue messages...")

    # using a set bc...
    # 1. mqclient doesn't guarantee deliver-once delivery
    # 2. assuming (without domain knowledge) that result values are unique
    got: set[Any] = set()
    # alternatively, we could adjust the timeout though that requires other assumptions

    async with queue.open_sub() as sub:
        i = 0
        async for msg in sub:
            LOGGER.debug(f"received #{i}: {msg}")
            got.add(msg)
            i += 1
            if len(got) == len(MSGS):  # naive check (see above explanation)
                break

    LOGGER.info("Done reading queue")


def monitor_wms(rc: RestClient, workflow_id: str) -> None:
    """Routinely query WMS."""
    LOGGER.info("Monitoring WMS...")

    prev_workflow = {}  # type: ignore
    prev_task_directives = []  # type: ignore
    prev_taskforces = []  # type: ignore

    for i in itertools.count():
        if i > 0:
            time.sleep(15)  # in thread, so ok

        workflow = rc.request_seq(
            "GET",
            f"/v0/workflows/{workflow_id}",
        )
        task_directives = rc.request_seq(
            "POST",
            "/v0/query/task-directives",
            {"query": {"workflow_id": workflow_id}},
        )["task_directives"]

        if i == 0:
            taskforces = rc.request_seq(
                "POST",
                "/v0/query/taskforces",
                {"query": {"workflow_id": workflow_id}},
            )["taskforces"]
        else:
            taskforces = rc.request_seq(
                "POST",
                "/v0/query/taskforces",
                {
                    "query": {"workflow_id": workflow_id},
                    "projection": [
                        "condor_complete_ts",
                        "phase",
                        "compound_statuses",
                        "top_task_errors",
                        "taskforce_uuid",
                        "task_id",
                    ],
                },
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
        "--pilot-cvmfs-image-tag",
        required=True,
        help="the tag (version) of the pilot example image that the workers will use. Ex: 0.1.11",
    )
    parser.add_argument(
        "--n-workers",
        default=5,
        type=int,
        help="the number of workers to use",
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

    # request workflow
    workflow_id, input_queue, output_queue = await request_workflow(
        rc,
        args.pilot_cvmfs_image_tag,
        args.n_workers,
    )
    threading.Thread(
        target=monitor_wms,
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
    await load_queue(
        queue=Queue(
            input_mqprofile["broker_type"],
            address=input_mqprofile["broker_address"],
            name=input_mqprofile["mqid"],
            auth_token=input_mqprofile["auth_token"],
        )
    )
    output_mqprofile = next(p for p in mqprofiles if p["mqid"] == output_queue)
    await read_queue(
        queue=Queue(
            output_mqprofile["broker_type"],
            address=output_mqprofile["broker_address"],
            name=output_mqprofile["mqid"],
            auth_token=output_mqprofile["auth_token"],
            timeout=60 * 20,
        )
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
