"""Interface to backlog collection in the mongo database."""


import logging

from motor.motor_asyncio import AsyncIOMotorClient

LOGGER = logging.getLogger(__name__)


class BacklogMongoClient:
    """A client for interacting with backlog entries."""

    def __init__(self, mongo_client: AsyncIOMotorClient) -> None:  # type: ignore[valid-type]
        self.mongo_client = mongo_client
