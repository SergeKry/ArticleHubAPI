import pytest


LOGIN_URL = "/api/auth/login/"


@pytest.mark.asyncio
async def test_login_success(client, registered_user):
    response = await client.post(
        LOGIN_URL,
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client, registered_user):
    response = await client.post(
        LOGIN_URL,
        json={
            "email": registered_user["email"],
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_login_wrong_email(client, registered_user):
    response = await client.post(
        LOGIN_URL,
        json={
            "email": "wrong@example.com",
            "password": registered_user["password"],
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_login_invalid_email_format(client):
    response = await client.post(
        LOGIN_URL,
        json={
            "email": "not-an-email",
            "password": "string123",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_missing_password(client):
    response = await client.post(
        LOGIN_URL,
        json={
            "email": "user@example.com",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_missing_email(client):
    response = await client.post(
        LOGIN_URL,
        json={
            "password": "string123",
        },
    )

    assert response.status_code == 422