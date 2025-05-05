from chat_bot.config import get_logger
from chat_bot.crud import get_user_chat_mode, set_user_chat_mode
from chat_bot.enums import ChatMode
from chat_bot.redis_client import redis_client

log = get_logger(__name__)


def cache_key_from_tg_id(tg_id: int) -> str:
    """Generate a cache key based on the Telegram ID."""
    return f"user_chat_mode:{tg_id}"


async def add_mode_to_cache(tg_id: int, chat_mode: ChatMode) -> bool:
    """Add the chat mode of a user to the cache."""
    try:
        await redis_client.setex(
            name=cache_key_from_tg_id(tg_id),
            time=3600,  # Set expiration time to 1 hour
            value=chat_mode.name,
        )
    except Exception:
        log.exception("Failed to set user chat mode in cache: %s", tg_id)
        return False
    else:
        log.info("User=%s chat_mode=%s updated in cache", tg_id, chat_mode.name)
        return True


async def get_chat_mode(tg_id: int) -> ChatMode:
    """Get the chat mode of a user by their Telegram ID.

    This function first checks the cache for the user's chat mode.
    If not found, it retrieves the chat mode from the database and updates the cache.

    Args:
        tg_id (int): Telegram user ID.

    Returns:
        ChatMode: The chat mode of the user.

    """
    log.info("Try to get user chat mode from cache: %s", tg_id)
    cache_value = await redis_client.get(cache_key_from_tg_id(tg_id))
    if cache_value:
        log.info("User=%s chat mode found in cache", tg_id)
        return ChatMode[cache_value]

    log.info("User tg_id=%s chat mode not found in cache, search the database", tg_id)
    chat_mode: ChatMode = await get_user_chat_mode(tg_id)

    cache_updated = await add_mode_to_cache(tg_id, chat_mode)
    if not cache_updated:
        return chat_mode

    log.info("User chat mode found and cached in database: %s", chat_mode)
    return chat_mode


async def set_chat_mode(tg_id: int, chat_mode: ChatMode) -> bool:
    """Set the chat mode of a user by their Telegram ID.

    Args:
        tg_id (int): Telegram user ID.
        chat_mode (ChatMode): Chat mode to set.

    Returns:
        bool: True if the chat mode was successfully set, False otherwise.

    """
    mode_updated = await set_user_chat_mode(tg_id, chat_mode)
    if not mode_updated:
        log.info("Failed to set user chat mode in database: %s", tg_id)
        return False

    log.info("User tg_id=%s new chat_mode=%s updated in database", tg_id, chat_mode)
    cache_updated = await add_mode_to_cache(tg_id, chat_mode)
    if not cache_updated:
        log.info("Failed to set user chat mode in cache: %s", tg_id)
        return False

    log.info("User tg_id=%s new chat_mode=%s updated in cache", tg_id, chat_mode)
    return True
