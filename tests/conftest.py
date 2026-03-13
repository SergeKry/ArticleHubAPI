import os
import uuid

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from pymongo import MongoClient

# Set test env BEFORE importing app modules
os.environ["APP_NAME"] = "FastAPI Mongo App Test"
os.environ["MONGO_ROOT_USERNAME"] = "admin"
os.environ["MONGO_ROOT_PASSWORD"] = "secret123"

# Use unique database name for each test session
test_db_name = f"myapp_test_{uuid.uuid4().hex[:8]}"
os.environ["MONGO_DB"] = test_db_name
os.environ["MONGO_HOST"] = "mongo"
os.environ["MONGO_PORT"] = "27017"

from app.config import settings
from app.main import create_app
from app.db import get_database


@pytest.fixture(scope="session", autouse=True)
def drop_test_database_after_session():
    yield

    client = MongoClient(settings.resolved_mongo_url)
    try:
        client.drop_database(test_db_name)
    finally:
        client.close()


@pytest_asyncio.fixture
async def app():
    application = create_app()
    async with LifespanManager(application):
        yield application


@pytest_asyncio.fixture(autouse=True)
async def clean_database(app):
    db = get_database()

    await db.users.delete_many({})
    await db.articles.delete_many({})
    await db.refresh_tokens.delete_many({})
    await db.email_notifications.delete_many({})

    yield

    await db.users.delete_many({})
    await db.articles.delete_many({})
    await db.refresh_tokens.delete_many({})
    await db.email_notifications.delete_many({})


@pytest_asyncio.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def registered_user(client):
    payload = {
        "email": "user@example.com",
        "password": "string123",
        "password_confirm": "string123",
        "name": "John Doe",
    }
    response = await client.post("/api/auth/register/", json=payload)
    assert response.status_code == 201
    return payload


@pytest_asyncio.fixture
async def auth_tokens(client, registered_user):
    response = await client.post(
        "/api/auth/login/",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    return response.json()