import json

from chat_bot.config import get_logger, settings
from chat_bot.redis_client import redis_client

log = get_logger(__name__)


async def add_message(key: str, value: str) -> bool:
    """Add a message to a Redis list and set its expiration time.

    Args:
        key (str): The key to add or update in Redis.
        value (str): The value to associate with the key.

    """
    try:
        # Add new value to the end of the list
        await redis_client.rpush(key, value)

        # Set the expiration time for the key
        await redis_client.expire(key, settings.REDIS_TTL_SECONDS)

        # Trim the list to keep only the last REDIS_MAX_MESSAGES items
        await redis_client.ltrim(key, -settings.REDIS_MAX_MESSAGES, -1)
    except Exception:
        log.exception(
            "Error adding key/value to Redis: key=%s, value=%s",
            key,
            value[:100],
        )
        return False
    else:
        return True


async def read_messages(key: str) -> list[dict]:
    """Read messages from a Redis list.

    Args:
        key (str): The key to read from Redis.

    Returns:
        list[dict]: The list of values associated with the key.

    """
    try:
        values: list = await redis_client.lrange(key, 0, -1)
        if not values:
            log.info("Key found, but empty: %s", key)
            return []
        log.info("Key found: %s", key)
        return [dict(json.loads(value)) for value in values]
    except Exception:
        log.exception("Error reading key from Redis: %s", key)
        return []


async def delete_messages(tg_id: int) -> bool:
    """Delete user messages from a Redis list.

    Args:
        tg_id (int): The Telegram ID of the user.

    """
    try:
        key = f"chat:{tg_id}:messages"
        await redis_client.delete(key)
    except Exception:
        log.exception("Error deleting key from Redis: %s", key)
        return False
    else:
        log.info("User messages deleted from Redis: %s", key)
        return True
