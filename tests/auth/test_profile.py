import pytest


PROFILE_URL = "/api/auth/profile/"


@pytest.mark.asyncio
async def test_profile_success(client, registered_user, auth_tokens):
    response = await client.get(
        PROFILE_URL,
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert set(data.keys()) == {"id", "email", "name"}
    assert data["email"] == registered_user["email"]
    assert data["name"] == registered_user["name"]
    assert isinstance(data["id"], str)
    assert data["id"]


@pytest.mark.asyncio
async def test_profile_without_token(client):
    response = await client.get(PROFILE_URL)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_profile_with_invalid_token(client):
    response = await client.get(
        PROFILE_URL,
        headers={
            "Authorization": "Bearer not-a-valid-token",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


@pytest.mark.asyncio
async def test_profile_with_refresh_token_fails(client, auth_tokens):
    response = await client.get(
        PROFILE_URL,
        headers={
            "Authorization": f"Bearer {auth_tokens['refresh_token']}",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"