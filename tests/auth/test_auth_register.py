import pytest


@pytest.mark.asyncio
async def test_register_user_success(client):
    payload = {
        "email": "user@example.com",
        "password": "string123",
        "password_confirm": "string123",
        "name": "John Doe",
    }

    response = await client.post("/api/auth/register/", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert data["email"] == "user@example.com"
    assert data["name"] == "John Doe"


@pytest.mark.asyncio
async def test_register_user_passwords_do_not_match(client):
    payload = {
        "email": "user@example.com",
        "password": "string123",
        "password_confirm": "string456",
        "name": "John Doe",
    }

    response = await client.post("/api/auth/register/", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Passwords do not match"


@pytest.mark.asyncio
async def test_register_user_duplicate_email(client):
    payload = {
        "email": "user@example.com",
        "password": "string123",
        "password_confirm": "string123",
        "name": "John Doe",
    }

    first_response = await client.post("/api/auth/register/", json=payload)
    second_response = await client.post("/api/auth/register/", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "User with this email already exists"


@pytest.mark.asyncio
async def test_register_user_invalid_email(client):
    payload = {
        "email": "not-an-email",
        "password": "string123",
        "password_confirm": "string123",
        "name": "John Doe",
    }

    response = await client.post("/api/auth/register/", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_user_missing_name(client):
    payload = {
        "email": "user@example.com",
        "password": "string123",
        "password_confirm": "string123",
    }

    response = await client.post("/api/auth/register/", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_user_short_password(client):
    payload = {
        "email": "user@example.com",
        "password": "123",
        "password_confirm": "123",
        "name": "John Doe",
    }

    response = await client.post("/api/auth/register/", json=payload)

    assert response.status_code == 422