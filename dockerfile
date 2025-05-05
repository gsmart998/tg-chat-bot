FROM python:3.13-slim

RUN apt-get update && apt-get install -y gcc libpq-dev && apt-get clean

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app

WORKDIR /app

RUN uv sync --locked

CMD ["uv", "run", "chat-bot"]
