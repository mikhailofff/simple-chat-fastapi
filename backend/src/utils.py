from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from .schemas.config import settings

from .exceptions import AuthenticationError


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


def create_jwt_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(data: dict):
    return create_jwt_token(data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))


def create_refresh_token(data: dict):
    return create_jwt_token(data, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        # todo custom error handling
        raise AuthenticationError()
    except InvalidTokenError:
        raise AuthenticationError()

    return payload

