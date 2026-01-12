import os
from contextlib import asynccontextmanager
import pytest_asyncio
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock
from asgi_lifespan import LifespanManager
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.routes.chat import router, limiter

from src.database.db import get_db
from src.database.models.base import Base


@pytest_asyncio.fixture()
async def redis_connection():
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.delete = AsyncMock(return_value=1)
    return mock_redis


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "test.db")

SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

TestingAsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def cleanup_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield 
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def db():
    async with TestingAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest_asyncio.fixture
async def app(db, redis_connection) -> FastAPI:
    @asynccontextmanager
    async def test_lifespan(_: FastAPI):
        await FastAPILimiter.init(redis_connection)
        yield
        await FastAPILimiter.close()
    
    app = FastAPI(lifespan=test_lifespan)
    app.include_router(router, prefix='/api')

    async def override_get_session():
        async with TestingAsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[limiter] = lambda: None
    app.dependency_overrides[get_db] = override_get_session

    return app


@pytest_asyncio.fixture
async def async_client(app: FastAPI) -> AsyncClient:
    async with LifespanManager(app) as manager:
        async with AsyncClient(transport=ASGITransport(app=manager.app), base_url="http://test") as client:
            yield client