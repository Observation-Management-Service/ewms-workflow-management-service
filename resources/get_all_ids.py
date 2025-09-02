"""Helper script to lookup all associated ids for a given id."""

import argparse
import asyncio
import json
import logging

from utils import get_rest_client

IDS = ["workflow_id", "task_id", "taskforce_uuid", "cluster_id"]

logging.getLogger().setLevel(logging.INFO)


async def main():
    parser = argparse.ArgumentParser(
        description="lookup all associated ids for a given id",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--ewms",
        dest="ewms_suffix",
        required=True,
        choices=["dev", "prod"],
        help="the suffix of the EWMS URL for the REST API (ex: ewms-dev -> https://ewms-dev.icecube.aq)",
    )
    parser.add_argument(
        "--workflow-id",
        "--wf",
        default="",
        help="the workflow's id",
    )
    parser.add_argument(
        "--task-id",
        "--tk",
        default="",
        help="the task's id",
    )
    parser.add_argument(
        "--taskforce-uuid",
        "--tf",
        default="",
        help="the taskforce's uuid",
    )
    parser.add_argument(
        "--cluster-id",
        "--cl",
        default=None,
        type=int,
        help="the cluster's id",
    )
    args = parser.parse_args()
    if not (query := {k: v for k, v in vars(args).items() if k in IDS and v}):
        raise ValueError("cannot find objects without at least one CL arg id")

    rc = get_rest_client(args.ewms_suffix)

    ####

    # taskforce has the most ids in it (most specific object)
    logging.info(f"{query=}")
    all_ids_on_tf = []
    after = None
    while True:
        resp = await rc.request(
            "POST",
            "/v1/query/taskforces",
            {
                "query": query,
                "projection": IDS,
                **({"after": after} if after else {}),  # only add if truthy
            },
        )
        all_ids_on_tf.extend(resp["taskforces"])
        if not (after := resp["next_after"]):
            break

    print(json.dumps(all_ids_on_tf, indent=4), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
    logging.info("Done.")
