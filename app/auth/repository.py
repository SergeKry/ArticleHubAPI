from datetime import datetime, UTC
from typing import Any

from app.db import get_users_collection


class AuthRepository:
    def __init__(self) -> None:
        self.collection = get_users_collection()

    async def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        return await self.collection.find_one({"email": email.lower()})

    async def create_user(
        self,
        *,
        email: str,
        hashed_password: str,
        name: str,
    ) -> dict[str, Any]:
        user_doc = {
            "email": email.lower(),
            "hashed_password": hashed_password,
            "name": name,
            "created_at": datetime.now(UTC),
        }

        result = await self.collection.insert_one(user_doc)
        created_user = await self.collection.find_one({"_id": result.inserted_id})

        if created_user is None:
            raise RuntimeError("User creation failed")

        return created_user

    async def create_indexes(self) -> None:
        await self.collection.create_index("email", unique=True)