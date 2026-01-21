"""Simple script to abort a workflow.

Useful for quick debugging in prod.
"""

import argparse
import asyncio
import json
import logging

from utils import get_rest_client

logging.getLogger().setLevel(logging.INFO)


async def main():
    parser = argparse.ArgumentParser(
        description="Abort a workflow",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "workflow_id",
        help="the workflow's id",
    )
    parser.add_argument(
        "--ewms",
        dest="ewms_suffix",
        required=True,
        choices=["dev", "prod"],
        help="the suffix of the EWMS URL for the REST API (ex: ewms-dev -> https://ewms-dev.icecube.aq)",
    )
    args = parser.parse_args()

    rc = get_rest_client(args.ewms_suffix)

    ####

    logging.info(f"aborting workflow {args.workflow_id}")
    resp = await rc.request(
        "POST",
        f"/v1/workflows/{args.workflow_id}/actions/abort",
    )
    print(json.dumps(resp, indent=4), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
    logging.info("Done.")
