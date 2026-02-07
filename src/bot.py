import json
import os
from pathlib import Path
from typing import Any

import boto3
import discord
import yt_dlp as youtube_dl
from botocore.exceptions import ClientError
from discord.ext import commands, tasks

# Silence useless bug reports messages


def _suppress_bug_reports(before: str = ";") -> str:
    return ""


youtube_dl.utils.bug_reports_message: Any = _suppress_bug_reports


def get_secret_file(fp: str) -> str:
    with open(fp) as f:
        secret = f.readline().strip()
    return secret


def get_secret_aws() -> str:
    secret_name = "dogbot_token_discord"
    region_name = "us-west-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e

    secret = get_secret_value_response["SecretString"]
    secret = json.loads(secret)
    secret = secret["DOGBOT_TOKEN_DISCORD"]

    return secret


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
    if token := os.getenv("DOGBOT_TOKEN_DISCORD"):
        return token

    secret_path = Path(__file__).resolve().parents[1] / "secret"
    return get_secret_file(str(secret_path))


bot = MyBot()
bot.run(get_discord_token())
