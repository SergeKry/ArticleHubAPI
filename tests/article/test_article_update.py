import pytest


CREATE_ARTICLE_URL = "/api/articles/"


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
async def test_update_article_success(client, auth_tokens):
    created_article = await create_article(
        client,
        auth_tokens["access_token"],
        title="Old title",
        content="Old content",
        tags=["python"],
    )

    response = await client.patch(
        f"/api/articles/{created_article['id']}/",
        json={
            "title": "New title",
            "content": "New content",
        },
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == created_article["id"]
    assert data["title"] == "New title"
    assert data["content"] == "New content"
    assert data["tags"] == ["python"]
    assert data["author"] == created_article["author"]
    assert data["created_at"] == created_article["created_at"]


@pytest.mark.asyncio
async def test_update_article_partial_success(client, auth_tokens):
    created_article = await create_article(
        client,
        auth_tokens["access_token"],
        title="Old title",
        content="Old content",
        tags=["python"],
    )

    response = await client.patch(
        f"/api/articles/{created_article['id']}/",
        json={"title": "Updated title"},
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Updated title"
    assert data["content"] == "Old content"


@pytest.mark.asyncio
async def test_update_article_without_token(client, auth_tokens):
    created_article = await create_article(
        client,
        auth_tokens["access_token"],
        title="Old title",
        content="Old content",
        tags=["python"],
    )

    response = await client.patch(
        f"/api/articles/{created_article['id']}/",
        json={"title": "Updated title"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_article_with_refresh_token_fails(client, auth_tokens):
    created_article = await create_article(
        client,
        auth_tokens["access_token"],
        title="Old title",
        content="Old content",
        tags=["python"],
    )

    response = await client.patch(
        f"/api/articles/{created_article['id']}/",
        json={"title": "Updated title"},
        headers={
            "Authorization": f"Bearer {auth_tokens['refresh_token']}",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


@pytest.mark.asyncio
async def test_update_article_forbidden_for_non_author(client, auth_tokens, registered_user):
    # Create article with first user
    created_article = await create_article(
        client,
        auth_tokens["access_token"],
        title="Original title",
        content="Original content",
        tags=["python"],
    )

    # Create second user and get their tokens
    second_user_payload = {
        "email": "second@example.com",
        "password": "string123",
        "password_confirm": "string123",
        "name": "Second User",
    }
    await client.post("/api/auth/register/", json=second_user_payload)
    
    second_user_tokens_response = await client.post(
        "/api/auth/login/",
        json={
            "email": second_user_payload["email"],
            "password": second_user_payload["password"],
        },
    )
    assert second_user_tokens_response.status_code == 200
    second_user_tokens = second_user_tokens_response.json()

    response = await client.patch(
        f"/api/articles/{created_article['id']}/",
        json={"title": "Hacked title"},
        headers={
            "Authorization": f"Bearer {second_user_tokens['access_token']}",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You are not allowed to edit this article"


@pytest.mark.asyncio
async def test_update_article_not_found(client, auth_tokens):
    response = await client.patch(
        "/api/articles/non-existent-id/",
        json={"title": "Updated title"},
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid article ID format"


@pytest.mark.asyncio
async def test_update_article_empty_payload_fails(client, auth_tokens):
    created_article = await create_article(
        client,
        auth_tokens["access_token"],
        title="Old title",
        content="Old content",
        tags=["python"],
    )

    response = await client.patch(
        f"/api/articles/{created_article['id']}/",
        json={},
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_article_cannot_change_tags(client, auth_tokens):
    created_article = await create_article(
        client,
        auth_tokens["access_token"],
        title="Old title",
        content="Old content",
        tags=["python"],
    )

    response = await client.patch(
        f"/api/articles/{created_article['id']}/",
        json={"tags": ["django"]},
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}",
        },
    )

    assert response.status_code == 422