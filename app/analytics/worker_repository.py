from datetime import datetime, timezone
from typing import Any

from pymongo import MongoClient

from app.config import settings


class AnalyticsWorkerRepository:
    def __init__(self) -> None:
        self.client = MongoClient(settings.mongo_url)
        self.db = self.client[settings.mongo_db]
        self.articles = self.db["articles"]
        self.snapshots = self.db["analytics_snapshots"]

    def count_articles(self) -> int:
        return self.articles.count_documents({})

    def create_snapshot(
        self,
        *,
        metric: str,
        value: int,
    ) -> dict[str, Any]:
        doc = {
            "metric": metric,
            "value": value,
            "created_at": datetime.now(timezone.utc),
        }
        result = self.snapshots.insert_one(doc)
        created_doc = self.snapshots.find_one({"_id": result.inserted_id})
        if created_doc is None:
            raise RuntimeError("Snapshot creation failed")
        return created_doc

    def close(self) -> None:
        self.client.close()