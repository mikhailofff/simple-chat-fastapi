import logging
from typing import Any

import redis.asyncio as redis

from ..config import REDIS_HOST, REDIS_PORT

logger = logging.getLogger(__name__)


def get_redis_connection() -> Any:
    redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}"
    logger.debug("Initialized Redis connection")
    return redis.from_url(url=redis_url, decode_responses=True)  # type: ignore[no-untyped-call]
