from fastapi import APIRouter, Depends, Query, status, HTTPException, Response

from app.article.dependencies import get_article_service
from app.article.exceptions import ArticleNotFoundError, InvalidArticleIdError, ArticlePermissionDeniedError
from app.article.schemas import ArticleCreateRequest, ArticleResponse, ArticleShortResponse, ArticleUpdateRequest
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

@router.get(
    "/{id}/",
    response_model=ArticleResponse,
    status_code=status.HTTP_200_OK,
)
async def get_article(
    id: str,
    service: ArticleService = Depends(get_article_service),
):
    try:
        return await service.get_article(id)
    except InvalidArticleIdError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ArticleNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{id}/",
    response_model=ArticleResponse,
    status_code=status.HTTP_200_OK,
)
async def update_article(
    id: str,
    payload: ArticleUpdateRequest,
    token_payload: dict = Depends(get_current_access_token_payload),
    service: ArticleService = Depends(get_article_service),
):
    try:
        return await service.update_article(
            article_id=id,
            payload=payload,
            current_user_id=token_payload["sub"],
        )
    except ArticleNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ArticlePermissionDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except InvalidArticleIdError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_article(
    id: str,
    token_payload: dict = Depends(get_current_access_token_payload),
    service: ArticleService = Depends(get_article_service),
):
    try:
        await service.delete_article(
            article_id=id,
            current_user_id=token_payload["sub"],
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ArticleNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ArticlePermissionDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except InvalidArticleIdError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

@router.post(
    "/{id}/analyze/",
    status_code=status.HTTP_200_OK,
)
async def analyze_article(
    id: str,
    service: ArticleService = Depends(get_article_service),
):
    try:
        await service.analyze_article(article_id=id)
        return Response(status_code=status.HTTP_200_OK)
    except ArticleNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except InvalidArticleIdError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
