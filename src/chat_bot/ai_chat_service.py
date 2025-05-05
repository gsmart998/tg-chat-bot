import json

from chat_bot import prompts
from chat_bot.ai_chat_client import get_chatgpt_response
from chat_bot.config import get_logger
from chat_bot.enums import ChatMode
from chat_bot.redis_crud import add_message, read_messages

log = get_logger(__name__)


def get_base_prompt(mode: ChatMode) -> list[dict]:
    """Get the base prompt for the chat mode.

    Args:
        mode (ChatMode): The chat mode to use.

    Returns:
        list[dict]: A list containing the system message for the chat mode.

    """
    system_message: dict = {
        "role": "system",
        "content": (
            prompts.NEUTRAL
            if mode == ChatMode.NEUTRAL
            else prompts.CASUAL
            if mode == ChatMode.CASUAL
            else prompts.STRICT
        ),
    }
    return [system_message]


async def handle_user_message(
    tg_id: int,
    message_text: str,
    mode: ChatMode = ChatMode.NEUTRAL,
) -> None:
    """Handle user message and get response from OpenAI.

    Args:
        tg_id (int): The Telegram ID of the user.
        message_text (str): The message text from the user.
        mode (ChatMode): The chat mode to use.

    Returns:
        str: The response text from OpenAI.

    """
    log.debug("Current mode: %s", mode)
    key = f"chat:{tg_id}:messages"

    # 1. Save user message to Redis
    user_msg: str = json.dumps({"role": "user", "content": message_text})
    await add_message(key, user_msg)
    log.debug("Key: %s, Message: %s", key, user_msg)

    # 2. Prepare messages with system prompt
    messages: list = get_base_prompt(mode)

    # 3. Fetch previous messages from Redis
    redis_messages: list[dict] = await read_messages(key)
    if not redis_messages:
        messages.append(dict(user_msg))
    else:
        messages.extend(redis_messages)

    log.debug("\n\n\nMessages: %s\n\n\n", messages)

    # 4. Fetch response from OpenAI
    response_text = await get_chatgpt_response(messages)
    log.info("AI response: %s", response_text)

    # 5. Save response from OpenAI
    assistant_msg = {"role": "assistant", "content": response_text}
    await add_message(key, json.dumps(assistant_msg))
    log.debug("AI response saved")

    return response_text
