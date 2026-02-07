import os
from typing import Any

import discord
import yt_dlp as youtube_dl
from discord.ext import commands, tasks

# Silence useless bug reports messages


def _suppress_bug_reports(before: str = ";") -> str:
    return ""


youtube_dl.utils.bug_reports_message: Any = _suppress_bug_reports


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
        self.initial_extensions = ["cogs.music", "cogs.misc", "cogs.dota"]

    async def setup_hook(self):
        self.background_task.start()
        for ext in self.initial_extensions:
            await self.load_extension(ext)

    async def close(self):
        await super().close()

    @tasks.loop(minutes=10)
    async def background_task(self):
        print("Running background task...")

    async def on_ready(self):
        print("Ready!")


def get_discord_token() -> str:
    token = os.getenv("DOGBOT_TOKEN_DISCORD")
    if token:
        return token

    raise RuntimeError(
        "DOGBOT_TOKEN_DISCORD is not set. Put it in .env or export it in your shell."
    )


bot = MyBot()
bot.run(get_discord_token())
