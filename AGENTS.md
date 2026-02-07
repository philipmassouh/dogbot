# AGENTS

## Project

Dogbot is a personal Discord bot with music and Dota commands.

## Tooling

- Python/deps: `uv`
- Lint/format: `ruff`
- Type check: `ty`

## Setup

1. Install system deps:
   - macOS: `brew install ffmpeg opus`
   - Debian/Ubuntu: `sudo apt-get update && sudo apt-get install -y ffmpeg libopus0`
2. Install Python deps: `uv sync`

## Run

- `uv run python src/bot.py`

Token resolution order:

1. `DOGBOT_TOKEN_DISCORD` env var
2. `secret` file in repo root

## Quality checks

- `uv run ruff format .`
- `uv run ruff check . --fix`
- `uv run ty check`
