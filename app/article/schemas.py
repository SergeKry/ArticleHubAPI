from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class ArticleCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("title", "content")
    @classmethod
    def strip_text_fields(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty")
        return value

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str]) -> list[str]:
        normalized = []
        seen = set()

        for tag in tags:
            clean_tag = tag.strip().lower()
            if not clean_tag:
                continue
            if clean_tag not in seen:
                seen.add(clean_tag)
                normalized.append(clean_tag)

        return normalized


class ArticleResponse(BaseModel):
    id: str
    title: str
    content: str
    tags: list[str]
    author: str
    created_at: datetime


class ArticleShortResponse(BaseModel):
    id: str
    title: str
    tags: list[str]
    author: str