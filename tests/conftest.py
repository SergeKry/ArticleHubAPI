import os
import uuid

import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

# Set test env BEFORE importing app modules
os.environ["APP_NAME"] = "FastAPI Mongo App Test"
os.environ["MONGO_ROOT_USERNAME"] = "admin"
os.environ["MONGO_ROOT_PASSWORD"] = "secret123"
# Use unique database name for each test session
os.environ["MONGO_DB"] = f"myapp_test_{uuid.uuid4().hex[:8]}"
os.environ["MONGO_HOST"] = "mongo"
os.environ["MONGO_PORT"] = "27017"

from app.main import create_app
from app.db import get_database


@pytest_asyncio.fixture
async def app():
    application = create_app()
    async with LifespanManager(application):
        yield application


@pytest_asyncio.fixture(autouse=True)
async def clean_database(app):  # important: depend on app
    db = get_database()
    # Clear all collections before each test
    await db.users.delete_many({})
    await db.articles.delete_many({})
    await db.refresh_tokens.delete_many({})
    yield
    # Clear all collections after each test
    await db.users.delete_many({})
    await db.articles.delete_many({})
    await db.refresh_tokens.delete_many({})


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