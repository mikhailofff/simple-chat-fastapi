import logging
from datetime import datetime, timezone

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from ..config import DATABASE_URL
from ..exceptions import AuthenticationError, ChangingPasswordError, DuplicateUserError
from .models.base import Base
from .models.message import Message
from .models.user import User

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

engine = create_async_engine(
    url=DATABASE_URL, echo=True, echo_pool=True, pool_size=20, max_overflow=0, pool_recycle=3600, pool_pre_ping=True
)

SessionLocal = async_sessionmaker(bind=engine, autocommit=False, autoflush=False)


async def get_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            logger.exception("DB session error")
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_paginated_messages(session: AsyncSession, first_id: int, limit: int):
    stmt = select(Message).order_by(Message.id.desc()).limit(limit)

    if first_id:
        stmt = stmt.where(Message.id < first_id)

    result = await session.execute(stmt)
    messages = result.scalars().all()

    return messages[::-1]


async def create_message(session: AsyncSession, content: str, created_at: datetime, created_by: str):
    db_message = Message(content=content, created_at=created_at, created_by=created_by)

    session.add(db_message)
    await session.commit()
    await session.refresh(db_message)

    return db_message


async def delete_message_from_db(session: AsyncSession, id: int):
    stmt = select(Message).filter_by(id=id)
    result = await session.execute(stmt)
    message = result.scalar_one()

    if message:
        await session.delete(message)
        await session.commit()
        return True
    return False


async def update_message_from_db(session: AsyncSession, id: int, content: str):
    stmt = select(Message).filter_by(id=id)
    result = await session.execute(stmt)
    message = result.scalar_one()

    if message:
        message.content = content
        message.updated_at = datetime.now(timezone.utc)
        await session.commit()
        return True
    return False


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


async def get_by_username(session: AsyncSession, username: str):
    stmt = select(User).filter_by(username=username)
    result = await session.execute(stmt)
    user = result.scalars().first()

    return user


async def authenticate_user(session: AsyncSession, username: str, password: str):
    user = await get_by_username(session, username)
    if not user or not verify_password(password, user.hashed_password):
        raise AuthenticationError()
    return user


async def create_user(session: AsyncSession, username: str, password: str):
    hashed_password = get_password_hash(password)
    user = User(username=username, hashed_password=hashed_password)
    try:
        session.add(user)
        await session.commit()
        await session.refresh(user)
    except IntegrityError:
        await session.rollback()
        raise DuplicateUserError(username=user.username)

    return user


async def change_password_in_db(session: AsyncSession, username: str, old_password: str, new_password: str):
    user = await get_by_username(session, username)

    if not user or not verify_password(old_password, user.hashed_password):
        raise ChangingPasswordError(username=username)
    user.hashed_password = get_password_hash(new_password)
    await session.commit()

    return True
