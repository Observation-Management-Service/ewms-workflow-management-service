"""utils.py."""


import logging

from motor.motor_asyncio import AsyncIOMotorClient

LOGGER = logging.getLogger(__name__)


async def create_mongodb_client() -> AsyncIOMotorClient:  # type: ignore[valid-type]
    """explain."""


async def ensure_indexes(mongo_client: AsyncIOMotorClient) -> None:  # type: ignore[valid-type]
    """explain."""
