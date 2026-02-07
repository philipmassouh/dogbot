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

- macOS: `brew install ffmpeg`
- Debian/Ubuntu: `sudo apt-get update && sudo apt-get install -y ffmpeg`

2) Install Python dependencies:

```bash
uv sync
```

3) Run the bot:

```bash
just run
```

## Dev commands

```bash
just fmt
just lint
just typecheck
```

## Notes

- Set `DOGBOT_TOKEN_DISCORD` in `.env` (loaded by `just`) or export it in your shell.
- Music playback requires `ffmpeg`.

![counters](https://github.com/philipmassouh/dogbot/blob/master/demo_images/counters.png)
![winrate](https://github.com/philipmassouh/dogbot/blob/master/demo_images/winrate.png)
![music](https://github.com/philipmassouh/dogbot/blob/master/demo_images/music.png)
