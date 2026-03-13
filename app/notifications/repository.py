from typing import Any
from app.db import get_email_notifications_collection


class EmailNotificationRepository:
    def __init__(self) -> None:
        self.collection = get_email_notifications_collection()

    async def create_indexes(self) -> None:
        await self.collection.create_index("user_id")
        await self.collection.create_index("email")
        await self.collection.create_index("created_at")