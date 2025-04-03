"""Simple script to grab a workflow's objects.

Useful for quick debugging in prod.
"""

import argparse
import asyncio
import json
import logging

from rest_tools.client import RestClient, SavedDeviceGrantAuth

logging.getLogger().setLevel(logging.INFO)


def get_rest_client(ewms_url: str) -> RestClient:
    """Get REST client for talking to EWMS.

    This will present a QR code in the terminal for initial validation.
    """
    if "://" not in ewms_url:
        ewms_url = "https://" + ewms_url
    logging.info(f"connecting to {ewms_url}...")

    # NOTE: If your script will not be interactive (like a cron job),
    # then you need to first run your script manually to validate using
    # the QR code in the terminal.

    return SavedDeviceGrantAuth(
        ewms_url,
        token_url="https://keycloak.icecube.wisc.edu/auth/realms/IceCube",
        filename="device-refresh-token",
        client_id="ewms-dev-public",
        retries=10,
    )


async def main():
    parser = argparse.ArgumentParser(
        description="Get a workflow's manifest",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "workflow_id",
        help="the workflow's id",
    )
    parser.add_argument(
        "--ewms-url",
        required=True,
        help="the url to connect to a EWMS server",
    )
    args = parser.parse_args()

    rc = get_rest_client(args.ewms_url)

    ####

    logging.info(f"getting workflow object for workflow {args.workflow_id}")
    resp = await rc.request(
        "GET",
        f"/v1/workflows/{args.workflow_id}",
    )
    print(json.dumps(resp, indent=4), flush=True)

    logging.info(f"getting task directives for workflow {args.workflow_id}")
    resp = await rc.request(
        "POST",
        "/v1/query/task-directives",
        {"query": {"workflow_id": args.workflow_id}},
    )
    print(json.dumps(resp, indent=4), flush=True)

    logging.info(f"getting taskforce objects for workflow {args.workflow_id}")
    resp = await rc.request(
        "POST",
        "/v1/query/taskforces",
        {"query": {"workflow_id": args.workflow_id}},
    )
    print(json.dumps(resp, indent=4), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
    logging.info("Done.")
