import logging
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Check if .env file exists
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if not env_path.exists():
    msg = f".env file not found at {env_path}"
    raise FileNotFoundError(msg)


class Settings(BaseSettings):
    """Settings class for the application.

    It loads environment variables from a .env file and provides
    a method to get the database URL.
    """

    # Telegram Bot token
    BOT_TOKEN: str

    # OpenAI API settings
    API_KEY: str
    BASE_URL: str
    MODEL: str

    # PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Basic settings
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=env_path)

    def get_postgres_url(self) -> str:
        """Get the PostgreSQL database URL.

        Returns:
            str: PostgreSQL database URL.

        """
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()

# Logger configuration
Path("logs").mkdir(parents=True, exist_ok=True)

LOG_LEVEL = settings.LOG_LEVEL.upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/app.log"),
    ],
)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)


log = get_logger(__name__)
effective_level: str = logging.getLevelName(log.getEffectiveLevel())
log.debug("Configured LOG_LEVEL: %s", LOG_LEVEL)
log.info("Effective LOG_LEVEL: %s", effective_level)
