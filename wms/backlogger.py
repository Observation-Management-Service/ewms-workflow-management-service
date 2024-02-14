"""The daemon task that serves the backlog."""


import logging

from motor.motor_asyncio import AsyncIOMotorClient

LOGGER = logging.getLogger(__name__)


async def startup(mongo_client: AsyncIOMotorClient) -> None:  # type: ignore[valid-type]
    """Start up the daemon task."""
