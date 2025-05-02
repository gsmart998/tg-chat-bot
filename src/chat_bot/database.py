from datetime import datetime

from sqlalchemy import Integer, func, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)

from chat_bot.config import get_logger, settings

# Get configured logger
log = get_logger(__name__)
DATABASE_URL = settings.get_postgres_url()

# Create async engine for working with database
engine = create_async_engine(url=DATABASE_URL)

# Create session maker to interact with database
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Create table name from class name.

        The table name is the lowercase version of the class name with 's' at the end.
        """
        return cls.__name__.lower() + "s"


async def check_database_connection() -> None:
    """Check the connection to the database.

    Raises:
        OSError: If the database is not reachable.
        OperationalError: If there is an error in the connection.

    """
    log.info("Checking database connection...")
    try:
        async with async_session_maker() as session:
            stmt = text("SELECT 1")
            await session.execute(stmt)
        log.info("✅ Successful connection to the database")
    except (OSError, OperationalError) as e:
        log.exception("❌ Database connection error, exiting...")
        msg = "Database connection error"
        raise RuntimeError(msg) from e
