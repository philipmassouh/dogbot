import discord
import yt_dlp as youtube_dl
from discord.ext import commands, tasks

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ""
TOKEN, __GUILD = open("secrets.csv", "r").readlines()


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


bot = MyBot()
bot.run(TOKEN)
