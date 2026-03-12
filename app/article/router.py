from fastapi import APIRouter, Depends, Query, status

from app.article.dependencies import get_article_service
from app.article.schemas import ArticleCreateRequest, ArticleResponse, ArticleShortResponse
from app.article.service import ArticleService
from app.core.auth import get_current_access_token_payload

router = APIRouter(prefix="/articles", tags=["articles"])


@router.post(
    "/",
    response_model=ArticleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_article(
    payload: ArticleCreateRequest,
    token_payload: dict = Depends(get_current_access_token_payload),
    service: ArticleService = Depends(get_article_service),
):
    return await service.create_article(
        payload=payload,
        author_id=token_payload["sub"],
    )


@router.get(
    "/",
    response_model=list[ArticleShortResponse],
    status_code=status.HTTP_200_OK,
)
async def list_articles(
    search: str | None = Query(default=None, min_length=1),
    tag: str | None = Query(default=None, min_length=1),
    service: ArticleService = Depends(get_article_service),
):
    return await service.list_articles(
        search=search,
        tag=tag,
    )