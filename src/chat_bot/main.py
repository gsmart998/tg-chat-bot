import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.types.bot_command import BotCommand
from aiogram.utils import markdown

from chat_bot.config import get_logger, settings
from chat_bot.crud import create_user
from chat_bot.database import check_database_connection
from chat_bot.redis_client import check_redis_connection, redis_client

# Get configured logger
log = get_logger(__name__)

BOT_TOKEN = settings.BOT_TOKEN

# Initialize Bot instance with default bot properties which will be passed to all
# API calls
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


bot_commands = [
    BotCommand(command="start", description="start using the bot"),
    BotCommand(command="help", description="list of available commands"),
    BotCommand(command="reset", description="reset your chat history"),
    BotCommand(command="about", description="show information about the bot"),
    # optional commands
    # BotCommand(command="mode", description="change the mode of communication with the bot"),
    # BotCommand(command="voice", description="activate voice mode"),
]


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """Handle `/start` command."""
    username = markdown.hbold(message.from_user.full_name)
    await message.answer(
        text=f"Hello, {username}!\nWait a moment, I'm registering you.",
    )
    user_created: bool = await create_user(
        tg_id=message.chat.id,
        first_name=message.chat.first_name,
    )
    if user_created:
        await message.answer(
            text="You are registered, now you can start using the bot.",
        )
    else:
        await message.answer(text="Something went wrong, please try again later.")


@dp.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    """Handle `/help` command."""
    commands: list[BotCommand] = await bot.get_my_commands()
    if commands:
        text = "Here is the list of available commands:\n"
        for command in commands:
            text += f"/{command.command} - {command.description}\n"
        await message.answer(text=text)

    else:
        await message.answer(text="No commands available.")


@dp.message(Command("reset"))
async def command_reset_handler(message: Message) -> None:
    """Handle `/reset` command."""
    await message.answer(text="Resetting your chat history...")
    # TODO: implement reset functionality


@dp.message(Command("about"))
async def command_about_handler(message: Message) -> None:
    """Handle `/about` command."""
    await message.answer(text="Some information about the bot...")


@dp.message()
async def message_handler(message: Message) -> None:
    """Forward received message back to the sender."""
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def async_main() -> None:
    """Asynchronous entry point to start the bot.

    This function performs the following steps:
    1. Checks the connection to the database to ensure it is operational.
    2. Updates the bot's command list to provide users with available commands.
    3. Starts polling to listen for and handle incoming updates from Telegram.
    """
    # Check the connection to the database before starting the bot
    await check_database_connection()
    await check_redis_connection()
    try:
        # Update Bot commands list
        await bot.set_my_commands(commands=bot_commands)
        log.info("Bot commands have been updated")
    except Exception:
        log.exception("Bot commands have not been updated")

    # And the run events dispatching
    try:
        await dp.start_polling(bot)
    finally:
        await redis_client.aclose()
        log.info("Redis client session closed")


def main() -> None:
    """Run the main entry point for the bot.

    Call the asynchronous main logic via asyncio.
    """
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
