from fastapi import status
from fastapi.exceptions import HTTPException


class UserException(HTTPException):
    def __init__(self, status_code: int, detail: str, headers: str):
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers,
        )


class AuthenticationError(UserException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials for user",
            headers={
                "WWW-Authenticate": "Bearer",
                "X-Error-Code": "USER_IS_UNAUTHORIZED"
            },
        )


class DuplicateUserError(UserException):
    def __init__(self, username: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with username {username} already exists",
            headers={
                "X-Error-Code": "USER_DUPLICATE"
            },
        )


class ChangingPasswordError(UserException):
    def __init__(self, username: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"New password is not fit in validation or user with username {username} does not exist",
            headers={
                "X-Error-Code": "CHANGING_PASSWORD"
            },
        )
