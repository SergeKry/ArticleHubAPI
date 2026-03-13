from bson import ObjectId
from typing import Any

from app.article.repository import ArticleRepository
from app.article.schemas import ArticleCreateRequest, ArticleResponse, ArticleShortResponse, ArticleUpdateRequest
from app.article.exceptions import ArticleNotFoundError, InvalidArticleIdError, ArticlePermissionDeniedError


class ArticleService:
    def __init__(self, repository: ArticleRepository) -> None:
        self.repository = repository

    async def _get_article_and_object_id_or_raise(self, article_id: str) -> tuple[dict[str, Any], ObjectId]:
        """Helper method to convert string ID to ObjectId and get article or raise appropriate error."""
        try:
            article_object_id = ObjectId(article_id)
        except Exception:
            raise InvalidArticleIdError("Invalid article ID format")
        
        article = await self.repository.get_article_by_id(article_object_id)
        if article is None:
            raise ArticleNotFoundError("Article not found")
        
        return article, article_object_id

    async def create_article(
        self,
        payload: ArticleCreateRequest,
        author_id: str,
    ) -> ArticleResponse:
        created_article = await self.repository.create_article(
            title=payload.title,
            content=payload.content,
            tags=payload.tags,
            author_id=author_id,
        )

        return ArticleResponse(
            id=str(created_article["_id"]),
            title=created_article["title"],
            content=created_article["content"],
            tags=created_article["tags"],
            author=created_article["author"],
            created_at=created_article["created_at"],
        )

    async def list_articles(
        self,
        *,
        search: str | None = None,
        tag: str | None = None,
    ) -> list[ArticleShortResponse]:
        articles = await self.repository.list_articles(
            search=search,
            tag=tag,
        )

        return [
            ArticleShortResponse(
                id=str(article["_id"]),
                title=article["title"],
                tags=article["tags"],
                author=article["author"],
            )
            for article in articles
        ]

    async def get_article(self, article_id: str) -> ArticleResponse:
        article, _ = await self._get_article_and_object_id_or_raise(article_id)

        return ArticleResponse(
            id=str(article["_id"]),
            title=article["title"],
            content=article["content"],
            tags=article["tags"],
            author=article["author"],
            created_at=article["created_at"],
        )

    async def update_article(
        self,
        *,
        article_id: str,
        payload: ArticleUpdateRequest,
        current_user_id: str,
    ) -> ArticleResponse:
        article, article_object_id = await self._get_article_and_object_id_or_raise(article_id)

        if article["author"] != current_user_id:
            raise ArticlePermissionDeniedError("You are not allowed to edit this article")

        update_data = payload.model_dump(exclude_unset=True)
        updated_article = await self.repository.update_article(
            article_id=article_object_id,
            update_data=update_data,
        )
        if updated_article is None:
            raise ArticleNotFoundError("Article not found")

        return ArticleResponse(
            id=str(updated_article["_id"]),
            title=updated_article["title"],
            content=updated_article["content"],
            tags=updated_article["tags"],
            author=updated_article["author"],
            created_at=updated_article["created_at"],
        )

    async def delete_article(
        self,
        *,
        article_id: str,
        current_user_id: str,
    ) -> None:
        article, article_object_id = await self._get_article_and_object_id_or_raise(article_id)

        if article["author"] != current_user_id:
            raise ArticlePermissionDeniedError("You are not allowed to delete this article")

        deleted = await self.repository.delete_article(article_object_id)
        if not deleted:
            raise ArticleNotFoundError("Article not found")