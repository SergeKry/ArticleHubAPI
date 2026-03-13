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


def get_users_collection():
    return get_database()["users"]


def get_refresh_tokens_collection():
    return get_database()["refresh_tokens"]


def get_articles_collection():
    return get_database()["articles"]


def get_email_notifications_collection():
    return get_database()["email_notifications"]


def get_analytics_snapshots_collection():
    return get_database()["analytics_snapshots"]