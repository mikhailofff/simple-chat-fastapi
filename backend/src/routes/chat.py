import json
import logging
from typing import Annotated

from fastapi import APIRouter, Body, Cookie, Depends, HTTPException, Query, Response, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio.session import AsyncSession

from ..core.redis_client import get_redis_connection
from ..database.db import (
    authenticate_user,
    change_password_in_db,
    create_message,
    create_user,
    delete_message_from_db,
    get_db,
    get_paginated_messages,
    update_message_from_db,
)
from ..dependencies import get_current_user, limiter
from ..schemas.message import (
    CreateMessageRequest,
    CreateMessageResponse,
    DeleteMessageRequest,
    DeleteMessageResponse,
    MessageListResponse,
    UpdateMessageRequest,
    UpdateMessageResponse,
)
from ..schemas.user import (
    AccessTokenResponse,
    ChangeUserPasswordRequest,
    ChangeUserPasswordResponse,
    RefreshTokenResponse,
    UserRequest,
    UserResponse,
)
from ..utils import create_access_token, create_refresh_token, verify_token

CACHE_MESSAGES_PREFIX = "chat:messages:"

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self.activate_connections: dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, username: str) -> None:
        await websocket.accept()
        self.activate_connections[websocket] = username
        await self.broadcast_userlist()

    async def disconnect(self, websocket: WebSocket) -> None:
        del self.activate_connections[websocket]
        await self.broadcast_userlist()

    async def broadcast(self, message: str) -> None:
        for connection in self.activate_connections:
            await connection.send_text(message)

    async def broadcast_userlist(self) -> None:
        for connection in self.activate_connections:
            message = json.dumps({"userlist": list(self.activate_connections.values())})
            await connection.send_text(message)


manager = ConnectionManager()

router = APIRouter()


@router.post("/sign-up", dependencies=[Depends(limiter)])
async def sign_up(
    user_request: Annotated[UserRequest, Body],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """
    Register a new user account.
    """

    user = await create_user(session, user_request.username, user_request.password)
    user_response = UserResponse(id=user.id, username=user.username, hashed_password=user.hashed_password)

    logger.info("User registered")
    return user_response


@router.post("/token", dependencies=[Depends(limiter)])
async def login_for_access_and_refresh_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> AccessTokenResponse:
    """
    Authenticate user and return JWT access and refresh token.
    """

    user = await authenticate_user(session, form_data.username, form_data.password)
    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})
    token_response = AccessTokenResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

    logger.info("User authenticated")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="lax")
    return token_response


@router.post("/refresh", dependencies=[Depends(limiter)])
async def refresh_access_token(refresh_token: Annotated[str | None, Cookie()] = None) -> RefreshTokenResponse:
    """
    Refresh access token and return it
    """

    payload = verify_token(refresh_token)
    token_response = RefreshTokenResponse(
        access_token=create_access_token({"sub": payload.get("sub")}), token_type="bearer"
    )
    return token_response


@router.patch("/change-password", dependencies=[Depends(limiter)])
async def change_password(
    request: Annotated[ChangeUserPasswordRequest, Body],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ChangeUserPasswordResponse:
    """
    Change user password.
    Validates old password and updates to new password.
    """

    success = await change_password_in_db(session, request.username, request.old_password, request.new_password)

    logger.info("Password changed")
    return ChangeUserPasswordResponse(success=success)


@router.get("/messages", dependencies=[Depends(limiter), Depends(get_current_user)])
async def get_messages(
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db)],
    redis_connection: Annotated[Redis, Depends(get_redis_connection)],
    first_id: Annotated[int | None, Query()] = None,
    limit: Annotated[int, Query()] = 20,
) -> MessageListResponse:
    """
    Retrieve all messages from the chat.
    Returns a list of all messages with their details including id, sender, content, and timestamp.
    Results are cached in Redis for 1 hour.
    """

    cache_key_messages = CACHE_MESSAGES_PREFIX + "last_messages"
    if first_id:
        if first_id - 20 < 0:
            cache_key_messages = CACHE_MESSAGES_PREFIX + "1-" + str(first_id - 1)
        else:
            cache_key_messages = CACHE_MESSAGES_PREFIX + str(first_id - 20) + "-" + str(first_id - 1)

    cached_messages_json = await redis_connection.get(cache_key_messages)

    if cached_messages_json:
        cached_payload = json.loads(cached_messages_json)
        response.headers["X-Cache"] = "HIT"
        logger.debug("Messages cache hit")
        return MessageListResponse(**cached_payload)

    try:
        messages = await get_paginated_messages(session, first_id, limit)
        messages_response = MessageListResponse(messages=[message.to_pydantic() for message in messages])
        serialized = (
            messages_response.model_dump_json()
            if hasattr(messages_response, "model_dump_json")
            else json.dumps(jsonable_encoder(messages_response))
        )
        await redis_connection.set(cache_key_messages, serialized, ex=3600)

        response.headers["X-Cache"] = "MISS"
        logger.debug("Messages cache miss; fetched from DB and cached")
        return messages_response
    except Exception as e:
        logger.exception("Error fetching or caching messages")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-message", dependencies=[Depends(limiter), Depends(get_current_user)])
async def send_message(
    session: Annotated[AsyncSession, Depends(get_db)],
    redis_connection: Annotated[Redis, Depends(get_redis_connection)],
    message_request: Annotated[CreateMessageRequest, Body],
) -> CreateMessageResponse:
    """
    Create and send a new message to the chat.
    Validates message content and stores it in the database.
    Returns the ID of the created message. Invalidates message cache.
    """

    try:
        new_message = await create_message(
            session=session,
            content=message_request.content,
            created_at=message_request.created_at,
            created_by=message_request.created_by,
        )

        await redis_connection.flushdb()

        message_response = CreateMessageResponse(id=new_message.id)

        logger.info("Message created")
        return message_response
    except Exception as e:
        logger.exception("Error creating message")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/delete-message", dependencies=[Depends(limiter), Depends(get_current_user)])
async def delete_message(
    session: Annotated[AsyncSession, Depends(get_db)],
    redis_connection: Annotated[Redis, Depends(get_redis_connection)],
    message_request: Annotated[DeleteMessageRequest, Query()],
) -> DeleteMessageResponse:
    """
    Delete a specific message from the chat by its ID.
    Returns success status indicating whether the message was deleted.
    Invalidates message cache.
    """

    try:
        success = await delete_message_from_db(session, message_request.id)

        await redis_connection.flushdb()

        logger.info("Message deleted")
        return DeleteMessageResponse(success=success)
    except Exception as e:
        logger.exception("Error deleting message")
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/update-message", dependencies=[Depends(limiter), Depends(get_current_user)])
async def update_message(
    session: Annotated[AsyncSession, Depends(get_db)],
    redis_connection: Annotated[Redis, Depends(get_redis_connection)],
    message_request: Annotated[UpdateMessageRequest, Body],
) -> UpdateMessageResponse:
    """
    Update content field of a specific message from the chat by its ID.
    Returns success status indicating whether the message was updated.
    Invalidates message cache.
    """

    try:
        success = await update_message_from_db(session, message_request.id, message_request.content)

        keys = []
        async for key in redis_connection.scan_iter("chat:messages:*-*"):
            words = key.split(":")
            range = words[-1].split("-")
            keys.append((int(range[-2]), int(range[-1])))

        cache_key_messages = CACHE_MESSAGES_PREFIX + "last_messages"
        for key in keys:
            if key[0] <= message_request.id and message_request.id <= key[1]:
                cache_key_messages = CACHE_MESSAGES_PREFIX + str(key[0]) + "-" + str(key[1])
                break

        cached_messages_json = await redis_connection.get(cache_key_messages)
        cached_payload = json.loads(cached_messages_json)
        for message in cached_payload["messages"]:
            if message["id"] == message_request.id:
                message["content"] = message_request.content
                break
        serialized = json.dumps(cached_payload)
        await redis_connection.set(cache_key_messages, serialized, ex=3600)

        logger.info("Message updated")
        return UpdateMessageResponse(success=success)
    except Exception as e:
        logger.exception("Error updating message")
        raise HTTPException(status_code=400, detail=str(e))


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, username: Annotated[str, Query]) -> None:
    """
    WebSocket endpoint for real-time chat functionality.
    Establishes connection for live message broadcasting and user status updates.
    Requires username as query parameter for user identification.
    """

    logger.info(f"WebSocket connection attempt for user: {username}")
    await manager.connect(websocket, username)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user: {username}")
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error for user {username}: {e}")
        await manager.disconnect(websocket)
