from pydantic import BaseModel, Field


class AccessTokenResponse(BaseModel):
    access_token: str = Field(description="JWT access token for authenticated requests")
    refresh_token: str = Field(description="JWT refresh token for authenticated requests")
    token_type: str = Field(description="Token type, typically 'bearer'")


class RefreshTokenResponse(BaseModel):
    access_token: str = Field(description="new JWT access token for authenticated requests")
    token_type: str = Field(description="Token type, typically 'bearer'")


class TokenData(BaseModel):
    username: str | None = Field(default=None, description="Username from JWT token")


class UserRequest(BaseModel):
    username: str = Field(description="Unique username for the user")
    password: str = Field(min_length=8, description="User password, minimum 8 characters")


class UserResponse(BaseModel):
    id: int = Field(description="The number in the database")
    username: str = Field(description="User's username")
    hashed_password: str = Field(description="Hashed password (for internal use)")


class ChangeUserPasswordRequest(BaseModel):
    username: str = Field(description="The name of the user which wants to change password")
    old_password: str = Field(...)
    new_password: str = Field(min_length=8)


class ChangeUserPasswordResponse(BaseModel):
    success: bool = Field(description="The flag of the successfully change password action")