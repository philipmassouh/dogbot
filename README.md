# Dogbot

Dogbot is a personal multipurpose Discord bot.

## Commands

### Music
- `!play <query-or-url>`
- `!queue <query-or-url>`
- `!view_queue`
- `!skip`
- `!leave`

### Dota
- `!dota_counters <hero>`
- `!dota_wr <hero>`

## Local setup (uv + Astral stack)

1) Install system dependencies:

- macOS: `brew install ffmpeg opus`
- Debian/Ubuntu: `sudo apt-get update && sudo apt-get install -y ffmpeg libopus0`

2) Install Python dependencies:

```bash
uv sync
```

3) Run the bot:

```bash
uv run python src/bot.py
```

## Dev commands

```bash
uv run ruff format .
uv run ruff check . --fix
uv run ty check
```

## Notes

- Set `DOGBOT_TOKEN_DISCORD`, or place the token in a `secret` file at the repo root.
- Music playback requires both `ffmpeg` and an available `opus` library.

![counters](https://github.com/philipmassouh/dogbot/blob/master/demo_images/counters.png)
![winrate](https://github.com/philipmassouh/dogbot/blob/master/demo_images/winrate.png)
![music](https://github.com/philipmassouh/dogbot/blob/master/demo_images/music.png)
