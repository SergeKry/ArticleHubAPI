from typing import Any

from bson import ObjectId
from pymongo import MongoClient

from app.config import settings


class ArticleWorkerRepository:
    def __init__(self) -> None:
        self.client = MongoClient(settings.resolved_mongo_url)
        self.collection = self.client[settings.mongo_db]["articles"]

    def attach_analysis(
        self,
        *,
        article_id: str,
        analysis: dict[str, Any],
    ) -> None:
        self.collection.update_one(
            {"_id": ObjectId(article_id)},
            {"$set": {"analysis": analysis}},
        )

    def close(self) -> None:
        self.client.close()