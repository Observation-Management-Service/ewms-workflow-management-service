"""Start server as application."""


import asyncio
import logging

from . import database, server
from .config import ENV, config_logging

LOGGER = logging.getLogger(__package__)


async def main() -> None:
    """Establish connections and start components."""

    # Mongo client
    LOGGER.info("Setting up Mongo client...")
    mongo_client = await database.utils.create_mongodb_client()
    await database.utils.ensure_indexes(mongo_client)
    LOGGER.info("Mongo client connected.")

    async with asyncio.TaskGroup() as tg:
        # launch_control
        LOGGER.info("Starting launch_control in background...")
        tg.create_task(launch_control.startup(mongo_client))

        # REST Server
        LOGGER.info("Setting up REST server...")
        rs = await server.make(mongo_client)
        rs.startup(address=ENV.REST_HOST, port=ENV.REST_PORT)  # type: ignore[no-untyped-call]
        tg.create_task(asyncio.Event().wait())

    await rs.stop()  # type: ignore[no-untyped-call]


if __name__ == "__main__":
    config_logging()
    asyncio.run(main())
