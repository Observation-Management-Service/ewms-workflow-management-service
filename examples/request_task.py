"""A simple example script (task) to send to EWMS.

See https://github.com/Observation-Management-Service/ewms-pilot/blob/main/examples/do_task.py
"""

import argparse
import asyncio
import itertools
import json
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, TYPE_CHECKING

import wipac_dev_tools.logging_tools

if TYPE_CHECKING:  # not installing dependency just for example script
    Queue = Any
else:
    from mqclient import Queue

from rest_tools.client import ClientCredentialsAuth, RestClient, SavedDeviceGrantAuth

LOGGER = logging.getLogger(__name__)


EWMS_PILOT_BROKER_CLIENT = "rabbitmq"

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


async def load_queue(task_in_queue: str, mq_token: str) -> None:
    """Load the in-queue's with several contents."""
    LOGGER.info("Loading in-queue with messages...")

    queue = Queue(
        EWMS_PILOT_BROKER_CLIENT,
        address=os.environ["EWMS_PILOT_BROKER_ADDRESS"],
        name=task_in_queue,
        auth_token=mq_token,
    )
    async with queue.open_pub() as pub:
        for i, msg in enumerate(MSGS):
            await pub.send(msg)
            LOGGER.debug(f"enqueued #{i}: {msg}")


async def request(
    rc: RestClient,
    pilot_cvmfs_image_tag: str,
    mq_token: str,
    n_workers: int,
) -> str:
    """Request EWMS (WMS) to process a task."""
    LOGGER.info("Requesting task to EWMS...")

    post_body = {
        "cluster_locations": ["sub-2"],
        "task_image": f"/cvmfs/icecube.opensciencegrid.org/containers/ewms/observation-management-service/ewms-pilot:{pilot_cvmfs_image_tag}",
        "task_args": "python /app/examples/do_task.py",
        "environment": {
            "EWMS_PILOT_BROKER_ADDRESS": os.environ["EWMS_PILOT_BROKER_ADDRESS"],
            "EWMS_PILOT_BROKER_AUTH_TOKEN": mq_token,
            "EWMS_PILOT_BROKER_CLIENT": EWMS_PILOT_BROKER_CLIENT,
        },
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
    task_directive = await rc.request("POST", "/v0/task-directives", post_body)

    LOGGER.debug(json.dumps(task_directive))

    return task_directive["task_id"]  # type: ignore[no-any-return]


async def read_queue(task_out_queue: str, mq_token: str) -> None:
    """Read and dump the out-queue's contents."""
    LOGGER.info("Reading out-queue messages...")

    # using a set bc...
    # 1. mqclient doesn't guarantee deliver-once delivery
    # 2. assuming (without domain knowledge) that result values are unique
    got: set[Any] = set()
    # alternatively, we could adjust the timeout though that requires other assumptions

    queue = Queue(
        EWMS_PILOT_BROKER_CLIENT,
        address=os.environ["EWMS_PILOT_BROKER_ADDRESS"],
        name=task_out_queue,
        auth_token=mq_token,
        timeout=60 * 20,
    )
    async with queue.open_sub() as sub:
        i = 0
        async for msg in sub:
            LOGGER.debug(f"received #{i}: {msg}")
            got.add(msg)
            i += 1
            if len(got) == len(MSGS):  # naive check (see above explanation)
                break

    LOGGER.info("Done reading queue")


def monitor_wms(rc: RestClient, task_id: str) -> None:
    """Routinely query WMS."""
    LOGGER.info("Monitoring WMS...")

    prev_task_directive = {}  # type: ignore
    prev_taskforces = []  # type: ignore

    for i in itertools.count():
        if i > 0:
            time.sleep(15)

        task_directive = rc.request_seq(
            "GET",
            f"/v0/task-directives/{task_id}",
        )
        if i == 0:
            taskforces = rc.request_seq(
                "POST",
                "/v0/query/taskforces",
                {"query": {"task_id": task_id}},
            )
        else:
            taskforces = rc.request_seq(
                "POST",
                "/v0/query/taskforces",
                {
                    "query": {"task_id": task_id},
                    "projection": [
                        "condor_complete_ts",
                        "phase",
                        "compound_statuses",
                        "top_task_errors",
                        "taskforce_uuid",
                        "task_id",
                    ],
                },
            )

        if task_directive == prev_task_directive and taskforces == prev_taskforces:
            LOGGER.info("no change")
            continue
        prev_task_directive = task_directive
        prev_taskforces = taskforces

        LOGGER.info("TASK DIRECTIVE:")
        LOGGER.info(json.dumps(task_directive, indent=4))
        LOGGER.info("TASKFORCES:")
        LOGGER.info(json.dumps(taskforces["taskforces"], indent=4))

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

    mq_token = ClientCredentialsAuth(
        "",
        token_url="https://keycloak.icecube.wisc.edu/auth/realms/IceCube",
        client_id=os.environ["KEYCLOAK_CLIENT_ID_BROKER"],
        client_secret=os.environ["KEYCLOAK_CLIENT_SECRET_BROKER"],
    ).make_access_token()

    # request task
    task_id = await request(
        rc,
        args.pilot_cvmfs_image_tag,
        mq_token,
        args.n_workers,
    )
    threading.Thread(
        target=monitor_wms,
        args=(rc, task_id),
        daemon=True,
    ).start()

    # get queue ids
    LOGGER.info("getting queues...")
    queues: list[str] = []
    while not queues:
        await asyncio.sleep(10)
        queues = (
            await rc.request(
                "GET",
                f"/v0/task-directives/{task_id}",
                {"projection": ["queues"]},
            )
        )["queues"]
    LOGGER.info(f"{queues=}")

    # load & read queues
    await load_queue(queues[0], mq_token)
    await read_queue(queues[1], mq_token)

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
