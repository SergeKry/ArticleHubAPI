import pytest


LIST_ARTICLES_URL = "/api/articles/"
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
async def test_list_articles_empty(client):
    response = await client.get(LIST_ARTICLES_URL)

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_articles_returns_newest_first(client, auth_tokens):
    access_token = auth_tokens["access_token"]

    older_article = await create_article(
        client,
        access_token,
        title="Older article",
        content="First created article",
        tags=["python"],
    )

    newer_article = await create_article(
        client,
        access_token,
        title="Newer article",
        content="Second created article",
        tags=["fastapi"],
    )

    response = await client.get(LIST_ARTICLES_URL)

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["id"] == newer_article["id"]
    assert data[0]["title"] == "Newer article"
    assert data[1]["id"] == older_article["id"]
    assert data[1]["title"] == "Older article"


@pytest.mark.asyncio
async def test_list_articles_search_by_title(client, auth_tokens):
    access_token = auth_tokens["access_token"]

    await create_article(
        client,
        access_token,
        title="Learning FastAPI",
        content="Some generic content",
        tags=["python"],
    )
    await create_article(
        client,
        access_token,
        title="Django tutorial",
        content="Another text",
        tags=["django"],
    )

    response = await client.get(
        LIST_ARTICLES_URL,
        params={"search": "fastapi"},
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Learning FastAPI"


@pytest.mark.asyncio
async def test_list_articles_search_by_content(client, auth_tokens):
    access_token = auth_tokens["access_token"]

    await create_article(
        client,
        access_token,
        title="First article",
        content="This article explains MongoDB basics",
        tags=["database"],
    )
    await create_article(
        client,
        access_token,
        title="Second article",
        content="This article explains Docker basics",
        tags=["devops"],
    )

    response = await client.get(
        LIST_ARTICLES_URL,
        params={"search": "mongodb"},
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "First article"


@pytest.mark.asyncio
async def test_list_articles_filter_by_tag(client, auth_tokens):
    access_token = auth_tokens["access_token"]

    await create_article(
        client,
        access_token,
        title="FastAPI intro",
        content="Some text",
        tags=["python", "fastapi"],
    )
    await create_article(
        client,
        access_token,
        title="Django intro",
        content="Some text",
        tags=["python", "django"],
    )

    response = await client.get(
        LIST_ARTICLES_URL,
        params={"tag": "django"},
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Django intro"
    assert data[0]["tags"] == ["python", "django"]


@pytest.mark.asyncio
async def test_list_articles_search_and_tag_filter(client, auth_tokens):
    access_token = auth_tokens["access_token"]

    await create_article(
        client,
        access_token,
        title="FastAPI with MongoDB",
        content="Building APIs with Python",
        tags=["python", "fastapi"],
    )
    await create_article(
        client,
        access_token,
        title="FastAPI with PostgreSQL",
        content="Building APIs with SQL",
        tags=["python", "database"],
    )
    await create_article(
        client,
        access_token,
        title="Django with MongoDB",
        content="Another article",
        tags=["django"],
    )

    response = await client.get(
        LIST_ARTICLES_URL,
        params={"search": "mongodb", "tag": "fastapi"},
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "FastAPI with MongoDB"
    assert data[0]["tags"] == ["python", "fastapi"]


@pytest.mark.asyncio
async def test_list_articles_is_public(client, auth_tokens):
    access_token = auth_tokens["access_token"]

    await create_article(
        client,
        access_token,
        title="Public article",
        content="Anyone can read this list",
        tags=["public"],
    )

    response = await client.get(LIST_ARTICLES_URL)

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Public article"