from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from chat_bot.config import get_logger, settings

log = get_logger(__name__)

# Initialize Redis client
redis_client: Redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
)


async def check_redis_connection() -> None:
    """Check the connection to the Redis server."""
    log.info("Checking Redis server connection...")
    try:
        response = await redis_client.ping()
        if response:
            log.info("✅ Successful connection to the Redis server")
        else:
            log.error("❌ Unexpected Redis response on PING: %s", response)
            msg: str = "Unexpected Redis response on PING"
            raise RuntimeError(msg)
    except (RedisConnectionError, RedisTimeoutError, OSError) as e:
        log.exception("❌ Redis server connection error, exiting...")
        msg: str = "Redis server connection error"
        raise RuntimeError(msg) from e
