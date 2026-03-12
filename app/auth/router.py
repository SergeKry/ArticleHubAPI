from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_auth_service
from app.auth.schemas import RegisterRequest, RegisterResponse
from app.auth.service import AuthService, UserAlreadyExistsError, PasswordMismatchError

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
    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except PasswordMismatchError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc