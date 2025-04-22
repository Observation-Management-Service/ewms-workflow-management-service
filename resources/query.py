#!/usr/bin/env python3

import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import Any

import wipac_dev_tools
from rest_tools.client import RestClient, SavedDeviceGrantAuth


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


async def query_ewms(
    rc: RestClient,
    kind: str,
    query: dict[str, Any],
    projection: list[str] | None,
):
    payload: dict[str, Any] = {"query": query}
    if projection:
        payload["projection"] = projection
    return await rc.request("POST", f"/v1/query/{kind}", payload)


def main():
    parser = argparse.ArgumentParser(description="Query EWMS /v1/query/* endpoint")
    parser.add_argument(
        "kind",
        choices=["workflows", "task-directives", "taskforces"],
    )
    parser.add_argument(
        "--query",
        required=True,
        type=json.loads,
        help="Mongo-style query (JSON string)",
    )
    parser.add_argument(
        "--projection",
        nargs="*",
        help="Fields to include (space-separated)",
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
    wipac_dev_tools.logging_tools.log_argparse_args(args)

    rc = get_rest_client(args.ewms_url)

    results = asyncio.run(query_ewms(rc, args.kind, args.query, args.projection))
    print(json.dumps(results, indent=4), flush=True)
    print(len(results), flush=True)
    for key in results.keys():
        print(f"{key}: {len(results[key])}")


if __name__ == "__main__":
    main()
