from fastapi import APIRouter, Depends, status

from app.article.dependencies import get_article_service
from app.article.schemas import ArticleCreateRequest, ArticleResponse
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