"""Start server as application."""


import asyncio
import logging

from . import backlogger, database, server
from .config import ENV, config_logging

LOGGER = logging.getLogger(__package__)


async def main() -> None:
    """Establish connections and start components."""

    # Mongo client
    LOGGER.info("Setting up Mongo client...")
    mongo_client = await database.utils.create_mongodb_client()
    indexing_task = asyncio.create_task(database.utils.ensure_indexes(mongo_client))
    await asyncio.sleep(0)  # start up previous task
    LOGGER.info("Mongo client connected.")

    # Backlogger
    LOGGER.info("Starting backlogger in background...")
    backlogger_task = asyncio.create_task(backlogger.startup(mongo_client))
    await asyncio.sleep(0)  # start up previous task

    # REST Server
    LOGGER.info("Setting up REST server...")
    rs = await server.make(mongo_client)
    rs.startup(address=ENV.REST_HOST, port=ENV.REST_PORT)  # type: ignore[no-untyped-call]
    try:
        await asyncio.Event().wait()
    finally:
        await rs.stop()  # type: ignore[no-untyped-call]
        indexing_task.cancel()
        backlogger_task.cancel()


if __name__ == "__main__":
    config_logging()
    asyncio.run(main())
