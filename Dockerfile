FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.5.30 /uv /uvx /bin/

WORKDIR /usr/src/app

COPY pyproject.toml README.md ./
RUN uv sync --no-dev

COPY src ./src
COPY demo_images ./demo_images

CMD ["uv", "run", "python", "src/bot.py"]
