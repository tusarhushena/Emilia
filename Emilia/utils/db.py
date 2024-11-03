__all__ = ["get_collection"]

from motor.core import AgnosticClient, AgnosticCollection, AgnosticDatabase
from motor.motor_asyncio import AsyncIOMotorClient

from Emilia import MONGO_DB_URL

_MGCLIENT: AgnosticClient = AsyncIOMotorClient(MONGO_DB_URL)

_DATABASE: AgnosticDatabase = _MGCLIENT["Emilia"]


def get_collection(name: str) -> AgnosticCollection:
    """Create or Get Collection from your database"""
    return _DATABASE[name]
