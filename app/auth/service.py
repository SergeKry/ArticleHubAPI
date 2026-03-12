from uuid import uuid4

from pymongo.errors import DuplicateKeyError

from app.auth.repository import AuthRepository
from app.auth.schemas import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LogoutRequest,
    ProfileResponse,
    RefreshRequest,
    TokenPairResponse,
)

from app.core.auth import (
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
)

from app.core.security import hash_password, verify_password


class UserAlreadyExistsError(Exception):
    pass


class PasswordMismatchError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidRefreshTokenError(Exception):
    pass


class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self.repository = repository

    async def register_user(self, payload: RegisterRequest) -> RegisterResponse:
        if payload.password != payload.password_confirm:
            raise PasswordMismatchError("Passwords do not match")

        existing_user = await self.repository.get_user_by_email(payload.email)
        if existing_user is not None:
            raise UserAlreadyExistsError("User with this email already exists")

        hashed_password = hash_password(payload.password)

        created_user = await self.repository.create_user(
            email=payload.email,
            hashed_password=hashed_password,
            name=payload.name,
        )

        return RegisterResponse(
            id=str(created_user["_id"]),
            email=created_user["email"],
            name=created_user["name"],
        )

    async def login(self, payload: LoginRequest) -> TokenPairResponse:
        user = await self.repository.get_user_by_email(payload.email)
        if user is None:
            raise InvalidCredentialsError("Invalid email or password")

        if not verify_password(payload.password, user["hashed_password"]):
            raise InvalidCredentialsError("Invalid email or password")

        access_token, _, _ = create_access_token(str(user["_id"]))
        refresh_token, refresh_jti, refresh_expires_at = create_refresh_token(str(user["_id"]))

        await self.repository.save_refresh_token(
            jti=refresh_jti,
            user_id=str(user["_id"]),
            raw_token=refresh_token,
            expires_at=refresh_expires_at,
        )

        return TokenPairResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh(self, payload: RefreshRequest) -> TokenPairResponse:
        token_payload = decode_token(payload.refresh_token)

        if token_payload.get("type") != TokenType.REFRESH:
            raise InvalidRefreshTokenError("Invalid refresh token")

        jti = token_payload.get("jti")
        user_id = token_payload.get("sub")

        if not jti or not user_id:
            raise InvalidRefreshTokenError("Invalid refresh token")

        stored_token = await self.repository.verify_refresh_token_record(
            jti=jti,
            raw_token=payload.refresh_token,
        )
        if stored_token is None:
            raise InvalidRefreshTokenError("Invalid refresh token")

        await self.repository.revoke_refresh_token(jti=jti)

        access_token, _, _ = create_access_token(user_id)
        new_refresh_token, new_refresh_jti, new_refresh_expires_at = create_refresh_token(user_id)

        await self.repository.save_refresh_token(
            jti=new_refresh_jti,
            user_id=user_id,
            raw_token=new_refresh_token,
            expires_at=new_refresh_expires_at,
        )

        return TokenPairResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

    async def logout(self, payload: LogoutRequest) -> None:
        token_payload = decode_token(payload.refresh_token)

        if token_payload.get("type") != TokenType.REFRESH:
            raise InvalidRefreshTokenError("Invalid refresh token")

        jti = token_payload.get("jti")
        if not jti:
            raise InvalidRefreshTokenError("Invalid refresh token")

        stored_token = await self.repository.verify_refresh_token_record(
            jti=jti,
            raw_token=payload.refresh_token,
        )
        if stored_token is None:
            raise InvalidRefreshTokenError("Invalid refresh token")

        await self.repository.revoke_refresh_token(jti=jti)

    async def get_profile(self, user_id: str) -> ProfileResponse:
        user = await self.repository.get_user_by_id(user_id)
        if user is None:
            raise InvalidCredentialsError("User not found")

        return ProfileResponse(
            id=str(user["_id"]),
            email=user["email"],
            name=user["name"],
        )