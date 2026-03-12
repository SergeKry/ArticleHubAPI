from datetime import datetime, UTC, timezone
from hashlib import sha256
from typing import Any
from bson import ObjectId

from pymongo.errors import DuplicateKeyError

from app.db import get_users_collection, get_refresh_tokens_collection


def _hash_token(raw_token:str) -> str:
    return sha256(raw_token.encode("utf-8")).hexdigest()


class AuthRepository:
    def __init__(self) -> None:
        self.users = get_users_collection()
        self.refresh_tokens = get_refresh_tokens_collection()

    async def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        return await self.users.find_one({"email": email.lower()})

    async def get_user_by_id(self, user_id: str) -> dict[str, Any] | None:
        return await self.users.find_one({"_id": ObjectId(user_id)})

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

        result = await self.users.insert_one(user_doc)
        created_user = await self.users.find_one({"_id": result.inserted_id})

        if created_user is None:
            raise RuntimeError("User creation failed")

        return created_user

    async def save_refresh_token(
        self,
        *,
        jti: str,
        user_id: str,
        raw_token: str,
        expires_at: datetime,
    ) -> None:
        await self.refresh_tokens.insert_one(
            {
                "jti": jti,
                "user_id": user_id,
                "token_hash": _hash_token(raw_token),
                "expires_at": expires_at,
                "created_at": datetime.now(timezone.utc),
                "revoked_at": None,
            }
        )

    async def get_refresh_token_record(
        self,
        *,
        jti: str,
    ) -> dict[str, Any] | None:
        return await self.refresh_tokens.find_one({"jti": jti})

    async def revoke_refresh_token(self, *, jti: str) -> None:
        await self.refresh_tokens.update_one(
            {"jti": jti},
            {"$set": {"revoked_at": datetime.now(timezone.utc)}},
        )

    async def verify_refresh_token_record(
        self,
        *,
        jti: str,
        raw_token: str,
    ) -> dict[str, Any] | None:
        return await self.refresh_tokens.find_one(
            {
                "jti": jti,
                "token_hash": _hash_token(raw_token),
                "revoked_at": None,
            }
        )

    async def create_indexes(self) -> None:
        await self.users.create_index("email", unique=True)
        await self.refresh_tokens.create_index("jti", unique=True)
        await self.refresh_tokens.create_index("user_id")
        await self.refresh_tokens.create_index("expires_at")