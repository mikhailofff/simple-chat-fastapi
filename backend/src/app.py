import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter

from .core.redis_client import get_redis_connection
from .exceptions import AuthenticationError, ChangingPasswordError, DuplicateUserError
from .routes.chat import router

logger = logging.getLogger(__name__)
loggerChat = logging.getLogger("src.chat")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, Any]:
    logger.info("Initializing rate limiter")
    await FastAPILimiter.init(get_redis_connection())
    yield
    logger.info("Closing rate limiter")
    await FastAPILimiter.close()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
    loggerChat.warning("Authentication failed: user not found or bad credentials")
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "detail": exc.detail,
            "error_code": exc.headers["X-Error-Code"] if exc.headers else None,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        },
    )


@app.exception_handler(DuplicateUserError)
async def duplicate_user_error_handler(request: Request, exc: DuplicateUserError) -> JSONResponse:
    loggerChat.warning("Registration failed: username duplicate")
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "detail": exc.detail,
            "error_code": exc.headers["X-Error-Code"] if exc.headers else None,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        },
    )


@app.exception_handler(ChangingPasswordError)
async def changing_password_error_handler(request: Request, exc: ChangingPasswordError) -> JSONResponse:
    logger.warning("Password change failed: validation or user mismatch")
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "detail": exc.detail,
            "error_code": exc.headers["X-Error-Code"] if exc.headers else None,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        },
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PATCH"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
