set dotenv-load := true

run:
    uv run python src/bot.py

fmt:
    uv run ruff format .

lint:
    uv run ruff check . --fix

typecheck:
    uv run ty check

check: lint typecheck
