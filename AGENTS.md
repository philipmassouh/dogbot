# AGENTS

## Project

Dogbot is a personal Discord bot with music and Dota commands.

## Tooling

- Python/deps: `uv`
- Lint/format: `ruff`
- Type check: `ty`

## Setup

1. Install system deps:
   - macOS: `brew install ffmpeg`
   - Debian/Ubuntu: `sudo apt-get update && sudo apt-get install -y ffmpeg`
2. Install Python deps: `uv sync`

## Run

- `just run`

Token source:

- `DOGBOT_TOKEN_DISCORD` env var (typically via `.env` with `just`)

## Quality checks

- `just fmt`
- `just lint`
- `just typecheck`
