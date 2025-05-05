# TG Chat Bot

TG Chat Bot is a lightweight, customizable Telegram bot designed to automate responses, integrate APIs, and enhance user interaction within Telegram chats. The bot is optimized for performance with asynchronous operations and caching mechanisms.

## Features

- Asynchronous Operation: The bot, database, and caching systems (Redis) all work asynchronously, ensuring faster responses and better scalability.

- Dependency Management with uv: The project uses uv, a Python package manager, to manage dependencies and ensure compatibility between libraries for smooth operation.

- Redis Caching: Frequently accessed data is cached in Redis, reducing response times and minimizing the load on external services and databases.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/gsmart998/tg-chat-bot.git
    cd tg-chat-bot
    
    ```

2. Set up your environment variables:
- Create a `.env` file in the root directory.
- Add your data:
    ```env
    BOT_TOKEN=your-telegram-bot-token
    API_KEY=your-openai-api-key
    MODEL=your-openai-model

    POSTGRES_USER=admin
    POSTGRES_PASSWORD=password

    REDIS_TTL_HOURS=12
    LOG_LEVEL=INFO

    # don't change next data:
    POSTGRES_DB=mydb
    POSTGRES_HOST=db
    REDIS_HOST=redis
    REDIS_PORT=6379
    REDIS_DB=0
    ```


3. Set up containers with commands:

```bash
docker-compose build  # Builds the containers
```

```bash
docker-compose run alembic  # Runs database migrations
```

```bash
docker-compose up  # Starts the bot and required services (DB, Redis)
```

## Usage

Send /start command to the bot, to start use it.

Here are the available commands:
```
/start – Start using the bot
/help – Show this list of commands
/reset – Reset your chat history
/about – Learn more about the bot
/mode – Change the communication mode (Casual, Neutral, or Strict)
```

## Configuration

You can customize the bot's behavior by editing the `config.py` file:

`REDIS_TTL_HOURS: int = 12` - time to live chat context

`REDIS_MAX_MESSAGES: int = 40` - maximum messages for openai context (user+assistant)


## Potential Improvements

Here are some ideas to enhance the bot further:

Improving Context Management with Tiktoken: Integrate Tiktoken to better manage token limits and optimize context usage for more accurate and efficient conversations.

Voice Command Support: Add the ability to process voice commands, expanding the bot's interaction capabilities.

Code Structure Improvement: Refactor the code for better modularity, maintainability, and readability, which could include separating concerns more clearly and improving naming conventions.
