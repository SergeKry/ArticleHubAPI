import pytest


CREATE_ARTICLE_URL = "/api/articles/"


async def register_user(
    client,
    *,
    email: str,
    password: str,
    name: str,
):
    response = await client.post(
        "/api/auth/register/",
        json={
            "email": email,
            "password": password,
            "password_confirm": password,
            "name": name,
        },
    )
    assert response.status_code == 201
    return response.json()


async def login_user(
    client,
    *,
    email: str,
    password: str,
):
    response = await client.post(
        "/api/auth/login/",
        json={
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 200
    return response.json()


async def create_article(
    client,
    access_token: str,
    *,
    title: str,
    content: str,
    tags: list[str],
):
    response = await client.post(
        CREATE_ARTICLE_URL,
        json={
            "title": title,
            "content": content,
            "tags": tags,
        },
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_delete_article_success(client, auth_tokens):
    created_article = await create_article(
        client,
        auth_tokens["access_token"],
        title="Delete me",
        content="Some content",
        tags=["python"],
    )

    response = await client.delete(
        f"/api/articles/{created_article['id']}/",
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}",
        },
    )

    assert response.status_code == 204
    assert response.text == ""

    get_response = await client.get(f"/api/articles/{created_article['id']}/")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_article_without_token(client, auth_tokens):
    created_article = await create_article(
        client,
        auth_tokens["access_token"],
        title="Delete me",
        content="Some content",
        tags=["python"],
    )

    response = await client.delete(f"/api/articles/{created_article['id']}/")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_article_with_refresh_token_fails(client, auth_tokens):
    created_article = await create_article(
        client,
        auth_tokens["access_token"],
        title="Delete me",
        content="Some content",
        tags=["python"],
    )

    response = await client.delete(
        f"/api/articles/{created_article['id']}/",
        headers={
            "Authorization": f"Bearer {auth_tokens['refresh_token']}",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


@pytest.mark.asyncio
async def test_delete_article_forbidden_for_non_author(client, auth_tokens):
    created_article = await create_article(
        client,
        auth_tokens["access_token"],
        title="Delete me",
        content="Some content",
        tags=["python"],
    )

    await register_user(
        client,
        email="second@example.com",
        password="string123",
        name="Second User",
    )
    second_user_tokens = await login_user(
        client,
        email="second@example.com",
        password="string123",
    )

    response = await client.delete(
        f"/api/articles/{created_article['id']}/",
        headers={
            "Authorization": f"Bearer {second_user_tokens['access_token']}",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You are not allowed to delete this article"


@pytest.mark.asyncio
async def test_delete_article_not_found(client, auth_tokens):
    response = await client.delete(
        "/api/articles/non-existent-id/",
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid article ID format"