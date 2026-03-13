# app/notifications/worker_repository.py
from datetime import datetime, timezone
from typing import Any

from pymongo import MongoClient
from app.config import settings


class EmailNotificationWorkerRepository:
    def __init__(self) -> None:
        self.client = MongoClient(settings.resolved_mongo_url)
        self.collection = self.client[settings.mongo_db]["email_notifications"]

    def create_email_log(
        self,
        *,
        user_id: str,
        email: str,
        subject: str,
        body: str,
    ) -> dict[str, Any]:
        doc = {
            "user_id": user_id,
            "email": email,
            "subject": subject,
            "body": body,
            "status": "created",
            "created_at": datetime.now(timezone.utc),
        }
        result = self.collection.insert_one(doc)
        created_doc = self.collection.find_one({"_id": result.inserted_id})
        if created_doc is None:
            raise RuntimeError("Email log creation failed")
        return created_doc

    def close(self) -> None:
        self.client.close()