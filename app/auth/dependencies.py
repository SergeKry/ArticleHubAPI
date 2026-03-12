from fastapi import Depends

from app.auth.repository import AuthRepository
from app.auth.service import AuthService


def get_auth_repository() -> AuthRepository:
    return AuthRepository()


def get_auth_service(
    repository: AuthRepository = Depends(get_auth_repository),
) -> AuthService:
    return AuthService(repository)