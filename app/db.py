from pymongo import AsyncMongoClient
from app.config import settings


class MongoDB:
    client: AsyncMongoClient | None = None


mongodb = MongoDB()


async def connect_to_mongo() -> None:
    mongodb.client = AsyncMongoClient(settings.mongo_url)


async def close_mongo_connection() -> None:
    if mongodb.client:
        await mongodb.client.close()
        mongodb.client = None


def get_database():
    if mongodb.client is None:
        raise RuntimeError("MongoDB client is not initialized")
    return mongodb.client[settings.mongo_db]