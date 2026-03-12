from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from bson import ObjectId

from app.db import get_database

router = APIRouter(prefix="/items", tags=["items"])


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class ItemResponse(BaseModel):
    id: str
    name: str
    description: str | None = None


@router.post("/", response_model=ItemResponse)
async def create_item(payload: ItemCreate):
    db = get_database()
    result = await db.items.insert_one(payload.model_dump())

    created = await db.items.find_one({"_id": result.inserted_id})
    if not created:
        raise HTTPException(status_code=500, detail="Item was not created")

    return ItemResponse(
        id=str(created["_id"]),
        name=created["name"],
        description=created.get("description"),
    )


@router.get("/", response_model=list[ItemResponse])
async def list_items():
    db = get_database()
    items = []

    cursor = db.items.find().sort("_id", -1)
    async for doc in cursor:
        items.append(
            ItemResponse(
                id=str(doc["_id"]),
                name=doc["name"],
                description=doc.get("description"),
            )
        )

    return items