import redis.asyncio as redis
import json
import logging
from app.config import settings

logger = logging.getLogger(__name__)

redis_client = None

async def get_redis():
    """Get Redis client (optional, for caching)"""
    global redis_client
    
    if not settings.USE_REDIS:
        return None
    
    if redis_client is None:
        try:
            redis_client = await redis.from_url(settings.REDIS_URL, decode_responses=True)
            await redis_client.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Redis not available (optional feature): {e}")
            redis_client = None
    
    return redis_client

async def set_cache(key: str, value: any, expire: int = 3600):
    """Set value in cache"""
    redis = await get_redis()
    if redis:
        try:
            await redis.setex(key, expire, json.dumps(value))
        except Exception as e:
            logger.error(f"Redis set failed: {e}")

async def get_cache(key: str):
    """Get value from cache"""
    redis = await get_redis()
    if redis:
        try:
            data = await redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Redis get failed: {e}")
    return None