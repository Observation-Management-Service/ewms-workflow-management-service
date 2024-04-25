"""A simple example script (task) to send to EWMS.

See https://github.com/Observation-Management-Service/ewms-pilot/blob/main/examples/do_task.py
"""


import argparse
import asyncio
import json
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # not installing dependency just for example script
    Queue = Any
else:
    from mqclient import Queue

from rest_tools.client import ClientCredentialsAuth, RestClient, SavedDeviceGrantAuth

LOGGER = logging.getLogger(__name__)
logging.getLogger("mqclient").setLevel(logging.INFO)
LOGGER.setLevel(logging.DEBUG)

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
    task_in_queue: str,
    task_out_queue: str,
    pilot_cvmfs_image_tag: str,
    mq_token: str,
    n_workers: int,
) -> str:
    """Request EWMS (WMS) to process a task."""
    LOGGER.info("Requesting task to EWMS...")

    post_body = dict(
        cluster_locations=["sub-2"],
        task_image=f"/cvmfs/icecube.opensciencegrid.org/containers/ewms/observation-management-service/ewms-pilot:{pilot_cvmfs_image_tag}",
        task_args=f"python /app/examples/do_task.py --queue-incoming {task_in_queue} --queue-outgoing {task_out_queue}",
        environment={
            "EWMS_PILOT_BROKER_ADDRESS": os.environ["EWMS_PILOT_BROKER_ADDRESS"],
            "EWMS_PILOT_BROKER_AUTH_TOKEN": mq_token,
            "EWMS_PILOT_BROKER_CLIENT": EWMS_PILOT_BROKER_CLIENT,
        },
        n_workers=n_workers,
        worker_config=dict(
            do_transfer_worker_stdouterr=True,
            max_worker_runtime=60 * 10,
            n_cores=1,
            priority=99,
            worker_disk="512M",
            worker_memory="512M",
        ),
    )
    task_directive = await rc.request("POST", "/task/directive", post_body)

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
    first = True
    while True:
        if first:
            resp = rc.request_seq(
                "POST",
                "/taskforces/find",
                {"query": {"task_id": task_id}},
            )
        else:
            resp = rc.request_seq(
                "POST",
                "/taskforces/find",
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
        LOGGER.info(json.dumps(resp["taskforces"][0], indent=4))
        first = False
        time.sleep(15)


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

    task_in_queue = Queue.make_name()
    task_out_queue = Queue.make_name()

    await load_queue(task_in_queue, mq_token)
    task_id = await request(
        rc,
        task_in_queue,
        task_out_queue,
        args.pilot_cvmfs_image_tag,
        mq_token,
        args.n_workers,
    )

    threading.Thread(
        target=monitor_wms,
        args=(rc, task_id),
        daemon=True,
    ).start()

    await read_queue(task_out_queue, mq_token)

    # wait at end, so monitor thread can get some final updates
    await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
