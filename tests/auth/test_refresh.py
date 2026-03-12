import pytest


REFRESH_URL = "/api/auth/refresh/"
LOGIN_URL = "/api/auth/login/"


@pytest.mark.asyncio
async def test_refresh_success(client, auth_tokens):
    response = await client.post(
        REFRESH_URL,
        json={"refresh_token": auth_tokens["refresh_token"]},
    )

    assert response.status_code == 200

    data = response.json()
    assert set(data.keys()) == {"access_token", "refresh_token", "token_type"}
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert isinstance(data["refresh_token"], str)
    assert data["access_token"]
    assert data["refresh_token"]


@pytest.mark.asyncio
async def test_refresh_with_invalid_token(client):
    response = await client.post(
        REFRESH_URL,
        json={"refresh_token": "not-a-valid-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] in {"Invalid token", "Invalid refresh token"}


@pytest.mark.asyncio
async def test_refresh_with_access_token_fails(client, auth_tokens):
    response = await client.post(
        REFRESH_URL,
        json={"refresh_token": auth_tokens["access_token"]},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"


@pytest.mark.asyncio
async def test_refresh_with_old_rotated_token_fails(client, auth_tokens):
    first_refresh = await client.post(
        REFRESH_URL,
        json={"refresh_token": auth_tokens["refresh_token"]},
    )
    assert first_refresh.status_code == 200

    second_refresh = await client.post(
        REFRESH_URL,
        json={"refresh_token": auth_tokens["refresh_token"]},
    )

    assert second_refresh.status_code == 401
    assert second_refresh.json()["detail"] == "Invalid refresh token"


@pytest.mark.asyncio
async def test_refresh_returns_new_token_pair(client, auth_tokens):
    response = await client.post(
        REFRESH_URL,
        json={"refresh_token": auth_tokens["refresh_token"]},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["access_token"] != auth_tokens["access_token"]
    assert data["refresh_token"] != auth_tokens["refresh_token"]


@pytest.mark.asyncio
async def test_refresh_with_missing_token_field(client):
    response = await client.post(
        REFRESH_URL,
        json={},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_refresh_with_wrong_payload_type(client):
    response = await client.post(
        REFRESH_URL,
        json={"refresh_token": 123},
    )

    assert response.status_code == 422