"""Simple script to grab a workflow's objects.

Useful for quick debugging in prod.
"""

import argparse
import asyncio
import json
import logging
from pathlib import Path

import wipac_dev_tools
from rest_tools.client import RestClient, SavedDeviceGrantAuth

logging.getLogger().setLevel(logging.INFO)


def get_rest_client(ewms_url: str) -> RestClient:
    """Get REST client for talking to EWMS.

    This will present a QR code in the terminal for initial validation.
    """
    logging.info(f"connecting to {ewms_url}...")

    # NOTE: If your script will not be interactive (like a cron job),
    # then you need to first run your script manually to validate using
    # the QR code in the terminal.

    prefix = ewms_url.lstrip("https://").split(".")[0]
    return SavedDeviceGrantAuth(
        ewms_url,
        token_url="https://keycloak.icecube.wisc.edu/auth/realms/IceCube",
        filename=str(Path(f"~/device-refresh-token-{prefix}").expanduser().resolve()),
        client_id=f"{prefix}-public",  # ex: ewms-prod-public
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
        type=lambda x: wipac_dev_tools.argparse_tools.validate_arg(
            x, x.startswith("https://"), ValueError("must start with https://")
        ),
        help="Base HTTPS URL to the EWMS REST API (ex: https://ewms-dev.icecube.aq)",
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
