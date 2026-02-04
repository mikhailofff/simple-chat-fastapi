from datetime import timedelta
from time import sleep

import pytest

from src.dependencies import get_current_user
from src.exceptions import AuthenticationError
from src.utils import create_access_token, create_jwt_token


def test_get_current_user() -> None:
    data = {"sub": "testname"}
    access_token = create_access_token(data)
    assert access_token is not None

    token_data = dict(get_current_user(access_token))
    assert token_data["username"] == "testname"


def test_get_current_user_with_invalid_token() -> None:
    with pytest.raises(AuthenticationError):
        access_token = "invalid_token"
        get_current_user(access_token)


def test_get_current_user_with_expired_token() -> None:
    with pytest.raises(AuthenticationError):
        data = {"sub": "testname"}
        expires_delta = timedelta(milliseconds=499)
        jwt_token = create_jwt_token(data, expires_delta)
        assert jwt_token is not None

        sleep(0.5)
        get_current_user(jwt_token)
