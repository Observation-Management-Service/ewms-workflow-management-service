"""request_task.py."""


import asyncio
import json
import logging
import os
from pathlib import Path

import mqclient as mq
from rest_tools.client import RestClient, SavedDeviceGrantAuth

LOGGER = logging.getLogger(__name__)

EWMS_PILOT_BROKER_CLIENT = "rabbitmq"


async def load_queue(task_in_queue: str) -> None:
    """Load the in-queue's with several contents."""
    msgs = [
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
        "orange",
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

    queue = mq.Queue(
        EWMS_PILOT_BROKER_CLIENT,
        address=os.environ["EWMS_PILOT_BROKER_ADDRESS"],
        name=task_in_queue,
    )
    async with queue.open_pub() as pub:
        for i, msg in enumerate(msgs):
            await pub.send(msg)
            LOGGER.debug(f"enqueued #{i}: {msg}")


async def request(rc: RestClient, task_in_queue: str, task_out_queue: str) -> str:
    """Request EWMS (WMS) to process a task."""
    post_body = dict(
        cluster_locations=["sub-2"],
        task_image="/cvmfs/icecube.opensciencegrid.org/containers/ewms/observation-management-service/ewms-task-management-service:0.1.11",
        task_args=f"python examples/do_task.py --queue-incoming {task_in_queue} --queue-outgoing {task_out_queue}",
        environment={
            "EWMS_PILOT_BROKER_ADDRESS": os.environ["EWMS_PILOT_BROKER_ADDRESS"],
            "EWMS_PILOT_BROKER_AUTH_TOKEN": os.environ["EWMS_PILOT_BROKER_AUTH_TOKEN"],
            "EWMS_PILOT_BROKER_CLIENT": EWMS_PILOT_BROKER_CLIENT,
        },
        n_workers=5,
        worker_config=dict(
            do_transfer_worker_stdouterr=False,
            max_worker_runtime=60 * 10,
            n_cores=1,
            priority=5,
            worker_disk="512M",
            worker_memory="512M",
        ),
    )
    task_directive = await rc.request("POST", "/task/directive", post_body)

    LOGGER.debug(json.dumps(task_directive))

    return task_directive["task_id"]  # type: ignore[no-any-return]


async def read_queue(task_out_queue: str) -> None:
    """Read and dump the out-queue's contents."""
    queue = mq.Queue(
        EWMS_PILOT_BROKER_CLIENT,
        address=os.environ["EWMS_PILOT_BROKER_ADDRESS"],
        name=task_out_queue,
    )
    async with queue.open_sub() as sub:
        i = 0
        async for msg in sub:
            LOGGER.debug(f"received #{i}: {msg}")
            i += 1

    LOGGER.info("Done reading queue")


async def monitor_wms(rc: RestClient, task_id: str) -> None:
    """Routinely query WMS."""
    while True:
        resp = await rc.request(
            "POST",
            "/taskforces/find",
            {"query": {"task_id": task_id}},
        )
        LOGGER.debug(json.dumps(resp, indent=4))
        await asyncio.sleep(30)


async def main() -> None:
    """explain."""
    rc = SavedDeviceGrantAuth(
        "https://ewms-dev.icecube.aq",
        token_url="https://keycloak.icecube.wisc.edu/auth/realms/IceCube",
        filename=str(Path("~/device-refresh-token").expanduser().resolve()),
        client_id="ewms-dev-public",
        retries=0,
    )

    task_in_queue = mq.Queue.make_name()
    task_out_queue = mq.Queue.make_name()

    if not os.getenv("EWMS_PILOT_BROKER_AUTH_TOKEN"):
        raise RuntimeError("EWMS_PILOT_BROKER_AUTH_TOKEN must be given")

    await load_queue(task_in_queue)
    task_id = await request(rc, task_in_queue, task_out_queue)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(read_queue(task_out_queue))
        tg.create_task(monitor_wms(rc, task_id))


if __name__ == "__main__":
    asyncio.run(main())
