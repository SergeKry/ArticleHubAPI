from app.article.repository import ArticleRepository
from app.article.schemas import ArticleCreateRequest, ArticleResponse, ArticleShortResponse


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