from datetime import datetime, timezone
from typing import Any
from bson import ObjectId

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

    async def list_articles(
        self,
        *,
        search: str | None = None,
        tag: str | None = None,
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {}

        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"content": {"$regex": search, "$options": "i"}},
            ]

        if tag:
            query["tags"] = tag.strip().lower()

        cursor = self.collection.find(
            query,
            {
                "_id": 1,
                "title": 1,
                "tags": 1,
                "author": 1,
            },
        ).sort("created_at", -1)

        return await cursor.to_list(length=None)

    async def get_article_by_id(self, article_id: ObjectId) -> dict[str, Any] | None:
        return await self.collection.find_one({"_id": article_id})

    async def update_article(
        self,
        *,
        article_id: ObjectId,
        update_data: dict[str, Any],
    ) -> dict[str, Any] | None:
        await self.collection.update_one(
            {"_id": article_id},
            {"$set": update_data},
        )
        return await self.collection.find_one({"_id": article_id})

    async def delete_article(self, article_id: ObjectId) -> bool:
        result = await self.collection.delete_one({"_id": article_id})
        return result.deleted_count > 0

    async def create_indexes(self) -> None:
        await self.collection.create_index("author")
        await self.collection.create_index("created_at")
        await self.collection.create_index("tags")