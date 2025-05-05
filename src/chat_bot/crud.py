from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chat_bot.config import get_logger
from chat_bot.database import async_session_maker
from chat_bot.enums import ChatMode
from chat_bot.models import User

# Get configured logger
log = get_logger(__name__)


async def get_user_by_tg_id(session: AsyncSession, tg_id: int) -> User | None:
    """Retrieve a user from the database by their Telegram ID.

    Args:
        session (AsyncSession): SQLAlchemy async session.
        tg_id (int): Telegram user ID.

    Returns:
        (User | None): User object if found, otherwise None.

    """
    stmt = select(User).where(User.tg_id == tg_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(tg_id: int, first_name: str) -> bool:
    """Create a new user in the database if the given Telegram ID does not exist.

    Args:
        tg_id (int): Telegram user ID.
        first_name (str): Telegram user's first name.

    Returns:
        bool: True if the user was created or already exists,
              False if an error occurred during execution.

    """
    log.info("Creating new user with tg_id=%s", tg_id)
    async with async_session_maker() as session:
        try:
            user = await get_user_by_tg_id(session=session, tg_id=tg_id)
            if user:
                log.info("User with tg_id=%s already exists", tg_id)
            else:
                new_user = User(tg_id=tg_id, first_name=first_name)
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
                log.info(
                    "User created: user_id=%s, tg_id=%s, first_name=%s",
                    new_user.id,
                    tg_id,
                    first_name,
                )
        except Exception:
            log.exception("Failed to create or check user")
            return False

        else:
            return True


async def set_user_chat_mode(tg_id: int, chat_mode: ChatMode) -> bool:
    """Set the chat mode of a user by their Telegram ID.

    Args:
        tg_id (int): Telegram user ID.
        chat_mode (ChatMode): Chat mode to set.

    Returns:
        bool: True if the chat mode was successfully set, False otherwise.

    """
    async with async_session_maker() as session:
        try:
            user = await get_user_by_tg_id(session=session, tg_id=tg_id)
            if not user:
                log.info("User with tg_id=%s not found", tg_id)
                return False
            user.chat_mode = chat_mode
            session.commit()
        except Exception:
            log.exception("Failed to set user chat mode")
            return False
        else:
            log.info("User chat mode updated: tg_id=%s, chat_mode=%s", tg_id, chat_mode)
            return True


async def get_user_chat_mode(tg_id: int) -> ChatMode:
    """Get the chat mode of a user by their Telegram ID.

    Args:
        tg_id (int): Telegram user ID.

    Returns:
        ChatMode: The chat mode of the user.

    """
    async with async_session_maker() as session:
        user = await get_user_by_tg_id(session=session, tg_id=tg_id)
        if user:
            log.info("User with tg_id=%s found, chat mode: %s", tg_id, user.chat_mode)
            return user.chat_mode
        log.info("User with tg_id=%s not found, defaulting to 'NEUTRAL'", tg_id)
        return ChatMode.NEUTRAL
