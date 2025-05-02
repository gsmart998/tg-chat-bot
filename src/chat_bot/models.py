from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from chat_bot.database import Base


class User(Base):
    """Model for storing user data in the database."""

    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str | None] = mapped_column(unique=True)

    def __init__(
        self,
        tg_id: int,
        first_name: str,
    ) -> None:
        """Initialize a User instance."""
        self.tg_id = tg_id
        self.first_name = first_name
