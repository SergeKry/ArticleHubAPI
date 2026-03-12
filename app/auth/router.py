from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.auth.dependencies import get_auth_service
from app.auth.schemas import (
    LoginRequest,
    LogoutRequest,
    ProfileResponse,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenPairResponse,
)
from app.auth.service import (
    AuthService,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    PasswordMismatchError,
    UserAlreadyExistsError,
)

from app.core.auth import get_current_access_token_payload

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register/",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    payload: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return await service.register_user(payload)
    except PasswordMismatchError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post(
    "/login/",
    response_model=TokenPairResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return await service.login(payload)
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.post(
    "/refresh/",
    response_model=TokenPairResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh(
    payload: RefreshRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return await service.refresh(payload)
    except InvalidRefreshTokenError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.post(
    "/logout/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    payload: LogoutRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        await service.logout(payload)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except InvalidRefreshTokenError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.get(
    "/profile/",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
)
async def profile(
    token_payload: dict = Depends(get_current_access_token_payload),
    service: AuthService = Depends(get_auth_service),
):
    try:
        return await service.get_profile(token_payload["sub"])
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc