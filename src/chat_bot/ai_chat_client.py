import openai

from chat_bot.config import get_logger, settings

log = get_logger(__name__)

client = openai.AsyncOpenAI(api_key=settings.API_KEY)


async def get_chatgpt_response(messages: list[str]) -> str:
    """Get response from OpenAI API.

    Args:
        messages (list[dict]): List of messages to send to the API.

    Returns:
        str: Response from the API.

    """
    completion = await client.chat.completions.create(
        model=settings.MODEL,
        messages=messages,
    )
    return completion.choices[0].message.content
