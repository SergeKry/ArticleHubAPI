from pydantic import BaseModel, EmailStr, Field, model_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    password_confirm: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=2, max_length=100)


class RegisterResponse(BaseModel):
    id: str
    email: EmailStr
    name: str