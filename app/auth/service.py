from app.auth.repository import AuthRepository
from app.auth.schemas import RegisterRequest, RegisterResponse
from app.core.security import hash_password


class UserAlreadyExistsError(Exception):
    pass


class PasswordMismatchError(Exception):
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