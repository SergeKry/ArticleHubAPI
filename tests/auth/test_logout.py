import pytest


LOGOUT_URL = "/api/auth/logout/"
REFRESH_URL = "/api/auth/refresh/"


@pytest.mark.asyncio
async def test_logout_success(client, auth_tokens):
    response = await client.post(
        LOGOUT_URL,
        json={"refresh_token": auth_tokens["refresh_token"]},
    )

    assert response.status_code == 204
    assert response.text == ""


@pytest.mark.asyncio
async def test_logout_with_invalid_token(client):
    response = await client.post(
        LOGOUT_URL,
        json={"refresh_token": "not-a-valid-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] in {"Invalid token", "Invalid refresh token"}


@pytest.mark.asyncio
async def test_logout_with_access_token_fails(client, auth_tokens):
    response = await client.post(
        LOGOUT_URL,
        json={"refresh_token": auth_tokens["access_token"]},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"


@pytest.mark.asyncio
async def test_logout_with_already_revoked_token_fails(client, auth_tokens):
    first_response = await client.post(
        LOGOUT_URL,
        json={"refresh_token": auth_tokens["refresh_token"]},
    )
    assert first_response.status_code == 204

    second_response = await client.post(
        LOGOUT_URL,
        json={"refresh_token": auth_tokens["refresh_token"]},
    )

    assert second_response.status_code == 401
    assert second_response.json()["detail"] == "Invalid refresh token"


@pytest.mark.asyncio
async def test_logout_with_missing_token_field(client):
    response = await client.post(
        LOGOUT_URL,
        json={},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_logout_with_wrong_payload_type(client):
    response = await client.post(
        LOGOUT_URL,
        json={"refresh_token": 123},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_logout_then_refresh_fails(client, auth_tokens):
    logout_response = await client.post(
        LOGOUT_URL,
        json={"refresh_token": auth_tokens["refresh_token"]},
    )
    assert logout_response.status_code == 204

    refresh_response = await client.post(
        REFRESH_URL,
        json={"refresh_token": auth_tokens["refresh_token"]},
    )

    assert refresh_response.status_code == 401
    assert refresh_response.json()["detail"] == "Invalid refresh token"


@pytest.mark.asyncio
async def test_logout_same_token_twice_fails(client, auth_tokens):
    first_response = await client.post(
        LOGOUT_URL,
        json={"refresh_token": auth_tokens["refresh_token"]},
    )
    assert first_response.status_code == 204

    second_response = await client.post(
        LOGOUT_URL,
        json={"refresh_token": auth_tokens["refresh_token"]},
    )

    assert second_response.status_code == 401
    assert second_response.json()["detail"] == "Invalid refresh token"