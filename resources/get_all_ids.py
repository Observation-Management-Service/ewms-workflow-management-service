"""Helper script to lookup all associated ids for a given id."""

import argparse
import asyncio
import json
import logging
from pathlib import Path

from rest_tools.client import RestClient, SavedDeviceGrantAuth

IDS = ["workflow_id", "task_id", "taskforce_uuid", "cluster_id"]

logging.getLogger().setLevel(logging.INFO)


def get_rest_client(ewms_suffix: str) -> RestClient:
    """Get REST client for talking to EWMS.

    This will present a QR code in the terminal for initial validation.
    """
    ewms_url = f"https://ewms-{ewms_suffix}.icecube.aq"
    logging.info(f"connecting to {ewms_url}...")

    # NOTE: If your script will not be interactive (like a cron job),
    # then you need to first run your script manually to validate using
    # the QR code in the terminal.

    return SavedDeviceGrantAuth(
        ewms_url,
        token_url="https://keycloak.icecube.wisc.edu/auth/realms/IceCube",
        filename=str(
            Path(f"~/device-refresh-token-ewms-{ewms_suffix}").expanduser().resolve()
        ),
        client_id=f"ewms-{ewms_suffix}-public",  # ex: ewms-prod-public
        retries=10,
    )


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
