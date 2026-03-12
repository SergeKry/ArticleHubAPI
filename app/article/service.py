from bson import ObjectId

from app.article.repository import ArticleRepository
from app.article.schemas import ArticleCreateRequest, ArticleResponse, ArticleShortResponse
from app.article.exceptions import ArticleNotFoundError, InvalidArticleIdError


class ArticleService:
    def __init__(self, repository: ArticleRepository) -> None:
        self.repository = repository

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
        try:
            article_object_id = ObjectId(article_id)
        except Exception:
            raise InvalidArticleIdError("Invalid article ID format")
        
        article = await self.repository.get_article_by_id(article_object_id)
        if article is None:
            raise ArticleNotFoundError("Article not found")

        return ArticleResponse(
            id=str(article["_id"]),
            title=article["title"],
            content=article["content"],
            tags=article["tags"],
            author=article["author"],
            created_at=article["created_at"],
        )