from fastapi import Depends

from app.article.repository import ArticleRepository
from app.article.service import ArticleService


def get_article_repository() -> ArticleRepository:
    return ArticleRepository()


def get_article_service(
    repository: ArticleRepository = Depends(get_article_repository),
) -> ArticleService:
    return ArticleService(repository)