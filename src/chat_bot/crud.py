from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chat_bot.config import get_logger
from chat_bot.database import async_session_maker
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
