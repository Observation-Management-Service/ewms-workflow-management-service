"""A script to request to the EWMS /v1/query/* endpoint(s)."""

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
    max_results: int | None,
    reverse: bool,
) -> list[dict[str, Any]]:
    payload: dict[str, Any] = {"query": query}
    if projection:
        payload["projection"] = projection

    main_key = kind.replace("-", "_")

    results: list = []
    next_after = None
    while True:
        resp = await rc.request(
            "POST",
            f"/v1/query/{kind}",
            {
                **payload,
                **({"after": next_after} if next_after else {}),
            },
        )
        logging.info(f"keys={len(resp.keys())}")
        for key in resp.keys():
            logging.info(
                f"{key}: {len(resp[key]) if isinstance(resp[key], dict | list) else resp[key]}"
            )
        logging.info(f'{resp["next_after"]=}')

        results += resp[main_key]
        if not (next_after := resp["next_after"]):
            break

    if reverse:
        results = results[::-1]
    if max_results:
        results = results[:max_results]

    return results


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
        "--max-results",
        type=int,
        default=None,
        help="Max number of results to return",
    )
    parser.add_argument(
        "--ewms-url",
        required=True,
        type=lambda x: wipac_dev_tools.argparse_tools.validate_arg(
            x, x.startswith("https://"), ValueError("must start with https://")
        ),
        help="Base HTTPS URL to the EWMS REST API (ex: https://ewms-dev.icecube.aq)",
    )
    parser.add_argument(
        "--reverse",
        action="store_true",
        help="Reverse the result order after retrieval (client-side only)",
    )
    args = parser.parse_args()
    wipac_dev_tools.logging_tools.log_argparse_args(args)

    rc = get_rest_client(args.ewms_url)

    results = asyncio.run(
        query_ewms(
            rc,
            args.kind,
            args.query,
            args.projection,
            args.max_results,
            args.reverse,
        )
    )
    print(json.dumps(results, indent=4), flush=True)
    logging.info(len(results))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
