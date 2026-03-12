import pytest


CREATE_ARTICLE_URL = "/api/articles/"


@pytest.mark.asyncio
async def test_create_article_success(client, auth_tokens):
    payload = {
        "title": "My first article",
        "content": "Some text",
        "tags": ["python", "django"],
    }

    response = await client.post(
        CREATE_ARTICLE_URL,
        json=payload,
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert set(data.keys()) == {
        "id",
        "title",
        "content",
        "tags",
        "author",
        "created_at",
    }
    assert data["title"] == payload["title"]
    assert data["content"] == payload["content"]
    assert data["tags"] == payload["tags"]
    assert isinstance(data["id"], str)
    assert data["id"]
    assert isinstance(data["author"], str)
    assert data["author"]
    assert isinstance(data["created_at"], str)
    assert data["created_at"]


@pytest.mark.asyncio
async def test_create_article_without_token(client):
    payload = {
        "title": "My first article",
        "content": "Some text",
        "tags": ["python", "django"],
    }

    response = await client.post(
        CREATE_ARTICLE_URL,
        json=payload,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_article_with_invalid_token(client):
    payload = {
        "title": "My first article",
        "content": "Some text",
        "tags": ["python", "django"],
    }

    response = await client.post(
        CREATE_ARTICLE_URL,
        json=payload,
        headers={
            "Authorization": "Bearer not-a-valid-token",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


@pytest.mark.asyncio
async def test_create_article_with_refresh_token_fails(client, auth_tokens):
    payload = {
        "title": "My first article",
        "content": "Some text",
        "tags": ["python", "django"],
    }

    response = await client.post(
        CREATE_ARTICLE_URL,
        json=payload,
        headers={
            "Authorization": f"Bearer {auth_tokens['refresh_token']}",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


@pytest.mark.asyncio
async def test_create_article_missing_title(client, auth_tokens):
    payload = {
        "content": "Some text",
        "tags": ["python", "django"],
    }

    response = await client.post(
        CREATE_ARTICLE_URL,
        json=payload,
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_article_missing_content(client, auth_tokens):
    payload = {
        "title": "My first article",
        "tags": ["python", "django"],
    }

    response = await client.post(
        CREATE_ARTICLE_URL,
        json=payload,
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_article_empty_title(client, auth_tokens):
    payload = {
        "title": "",
        "content": "Some text",
        "tags": ["python", "django"],
    }

    response = await client.post(
        CREATE_ARTICLE_URL,
        json=payload,
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_article_empty_content(client, auth_tokens):
    payload = {
        "title": "My first article",
        "content": "",
        "tags": ["python", "django"],
    }

    response = await client.post(
        CREATE_ARTICLE_URL,
        json=payload,
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_article_tags_default_to_empty_list(client, auth_tokens):
    payload = {
        "title": "My first article",
        "content": "Some text",
    }

    response = await client.post(
        CREATE_ARTICLE_URL,
        json=payload,
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["tags"] == []


@pytest.mark.asyncio
async def test_create_article_normalizes_tags(client, auth_tokens):
    payload = {
        "title": "My first article",
        "content": "Some text",
        "tags": ["Python", " django ", "python", ""],
    }

    response = await client.post(
        CREATE_ARTICLE_URL,
        json=payload,
        headers={
            "Authorization": f"Bearer {auth_tokens['access_token']}",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["tags"] == ["python", "django"]