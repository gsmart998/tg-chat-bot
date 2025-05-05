import asyncio

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.types.bot_command import BotCommand
from aiogram.utils import markdown
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pydantic import BaseModel

from chat_bot.ai_chat_service import handle_user_message
from chat_bot.config import get_logger, settings
from chat_bot.crud import create_user
from chat_bot.database import check_database_connection
from chat_bot.enums import ChatMode
from chat_bot.redis_client import check_redis_connection, redis_client
from chat_bot.redis_crud import delete_messages
from chat_bot.utils import get_chat_mode, set_chat_mode

# Get configured logger
log = get_logger(__name__)

BOT_TOKEN = settings.BOT_TOKEN

# Initialize Bot instance with default bot properties which will be passed to all
# API calls
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()
router = Router()
dp.include_router(router)

bot_commands = [
    BotCommand(command="start", description="start using the bot"),
    BotCommand(command="help", description="list of available commands"),
    BotCommand(command="reset", description="reset your chat history"),
    BotCommand(command="about", description="show information about the bot"),
    BotCommand(
        command="mode",
        description="change the mode of communication with the bot",
    ),
]


class ModeCallback(CallbackData, BaseModel, prefix="mode"):
    """Callback data for mode options.

    Attributes:
        mode (str): The selected mode of communication with the bot.

    """

    mode: str


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
            text=(
                "You are registered, now you can start using the bot.\n"
                "/about for more information."
            ),
        )
    else:
        await message.answer(text="Something went wrong, please try again later.")


@dp.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    """Handle `/help` command."""
    commands: list[BotCommand] = await bot.get_my_commands()
    if commands:
        text = "Here are the available commands\n\n"
        for command in commands:
            text += f"/{command.command} - {command.description}\n"
        await message.answer(text)

    else:
        await message.answer("No commands available.")


@dp.message(Command("reset"))
async def command_reset_handler(message: Message) -> None:
    """Handle `/reset` command."""
    wait_message: Message = await message.answer("Resetting your chat history...")
    if not await delete_messages(message.chat.id):
        await wait_message.edit_text(
            text="Failed to reset your chat history. Please try again later.",
        )
        return
    await wait_message.edit_text("Your chat history has been reset.")


@dp.message(Command("about"))
async def command_about_handler(message: Message) -> None:
    """Handle `/about` command."""
    await message.answer(
        text=(
            "About this bot\n\n"
            "This bot helps make your conversations easier, faster, and more "
            "personalized.\n"
            "Choose your communication style: Casual, Neutral, or Strict.\n"
            "Use /reset to clear history, /mode to switch style, and /help to see all "
            "commands.\n"
            "The bot adapts to your needs and makes chatting simple!"
        ),
    )


@dp.message(Command("mode"))
async def command_mode_handler(message: Message) -> None:
    """Handle `/mode` command."""
    user_mode: ChatMode = await get_chat_mode(message.chat.id)

    # Build inline keyboard with available modes
    builder = InlineKeyboardBuilder()
    for mode in ChatMode:
        builder.button(text=mode.value, callback_data=ModeCallback(mode=mode.name))
    builder.adjust(1)
    markup: InlineKeyboardMarkup = builder.as_markup()

    await message.answer(
        text=(
            f"Your current mode is: '{markdown.hbold(user_mode.value)}'\n"
            "Select a new mode of communication with the bot:"
        ),
        reply_markup=markup,
    )


@dp.message()
async def message_handler(message: Message) -> None:
    """Handle incoming messages.

    This function processes user messages and generates a response using the AI chat
    """
    if message.text is None:
        await message.answer(
            text="I can't process this message.\nPlease send me a text message.",
        )
        return

    wait_message: Message = await message.answer("Thinking 🤔")
    current_chat_mode: ChatMode = await get_chat_mode(message.chat.id)
    response = await handle_user_message(
        tg_id=message.chat.id,
        message_text=message.text,
        mode=current_chat_mode,
    )

    await wait_message.edit_text(
        text=response,
        parse_mode=None,
    )


@router.callback_query(ModeCallback.filter())
async def mode_callback_handler(
    query: CallbackQuery,
    callback_data: ModeCallback,
) -> None:
    """Handle mode callback query."""
    log.debug(callback_data)
    new_chat_mode: ChatMode = ChatMode[callback_data.mode]
    chat_mode_updated = await set_chat_mode(
        tg_id=query.from_user.id,
        chat_mode=new_chat_mode,
    )
    if not chat_mode_updated:
        await query.message.edit_text(
            text="Failed to update chat mode. Please try again later.",
        )
        return

    await query.message.edit_text(
        text=(
            "Your chat mode has been updated.\n"
            f"New mode: {markdown.hbold(new_chat_mode.value)}"
        ),
    )


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
        await bot.set_my_commands(bot_commands)
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
