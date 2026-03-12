from datetime import datetime, timezone
from typing import Any

from app.db import get_database


class ArticleRepository:
    def __init__(self) -> None:
        self.collection = get_database()["articles"]

    async def create_article(
        self,
        *,
        title: str,
        content: str,
        tags: list[str],
        author_id: str,
    ) -> dict[str, Any]:

        article_doc = {
            "title": title,
            "content": content,
            "tags": tags,
            "author": author_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        result = await self.collection.insert_one(article_doc)

        created_article = await self.collection.find_one({"_id": result.inserted_id})
        if created_article is None:
            raise RuntimeError("Article creation failed")

        return created_article

    async def create_indexes(self) -> None:
        await self.collection.create_index("author")
        await self.collection.create_index("created_at")
        await self.collection.create_index("tags")