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
async def test_get_article_success(client, auth_tokens):
    created_article = await create_article(
        client,
        auth_tokens["access_token"],
        title="My first article",
        content="Some text",
        tags=["python", "django"],
    )

    response = await client.get(f"/api/articles/{created_article['id']}/")

    assert response.status_code == 200

    data = response.json()
    assert set(data.keys()) == {
        "id",
        "title",
        "content",
        "tags",
        "author",
        "created_at",
    }
    assert data["id"] == created_article["id"]
    assert data["title"] == "My first article"
    assert data["content"] == "Some text"
    assert data["tags"] == ["python", "django"]
    assert data["author"] == created_article["author"]
    assert data["created_at"] == created_article["created_at"]


@pytest.mark.asyncio
async def test_get_article_not_found(client):
    response = await client.get("/api/articles/non-existent-id/")

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid article ID format"


@pytest.mark.asyncio
async def test_get_article_is_public(client, auth_tokens):
    created_article = await create_article(
        client,
        auth_tokens["access_token"],
        title="Public article",
        content="Anyone can open this",
        tags=["public"],
    )

    response = await client.get(f"/api/articles/{created_article['id']}/")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == created_article["id"]
    assert data["title"] == "Public article"