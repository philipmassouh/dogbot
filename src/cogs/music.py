import time
from datetime import timedelta

import discord
import yt_dlp
from discord.ext import commands

from music_constants import FFMPEG_OPTS, YTDLP_OPTS


class YoutubeSong:
    def __init__(
        self,
        title: str,
        url: str,
        uploader_name: str,
        uploader_url: str,
        duration: timedelta,
        thumbnail_url: str,
    ) -> None:
        self.title = title
        self.url = url
        self.uploader_name = uploader_name
        self.uploader_url = uploader_url
        self.duration = duration
        self.thumbnail_url = thumbnail_url

    @classmethod
    async def from_url(cls, link: str) -> "YoutubeSong":
        """
        Given a youtube url, extract metadata needed to display information
        and play the audio.
        """
        with yt_dlp.YoutubeDL(YTDLP_OPTS) as ydl:
            info = ydl.extract_info(link, download=False)
            if info is None:
                raise Exception("ydl unable to extract info")

        return cls(
            title=info.get("title:", "Title not found"),
            url=info["url"],
            uploader_name=info.get("uploader", "Uploader not found"),
            uploader_url=info.get("uploader_url", "Uploader not found"),
            duration=timedelta(
                seconds=float(info.get("duration", "Duration not found"))
            ),
            thumbnail_url=max(
                info["thumbnails"],
                key=lambda t: (t.get("width", 0), t.get("height", 0)),
            )["url"],
        )

    def build_yt_embed(self):
        embed = discord.Embed(
            title=self.title,
            url=self.url,
            description=f"**Now Playing**\nUploader: [{self.uploader_name}]({self.uploader_url})\nDuration: {self.duration}",
        )
        embed.set_image(url=self.thumbnail_url)
        return embed


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join_if_summoner_connected(self, ctx):
        """
        Join VC that command issuer is in.
        """
        if ctx.author.voice:
            self.voice_client = await ctx.author.voice.channel.connect()
        else:
            await ctx.send("You must be in a voice channel to summon me.")

    @commands.command()
    async def leave(self, ctx):
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
        else:
            await ctx.send("I'm not connected to a voice channel.")

    @commands.command("play_yt")
    async def play(self, ctx, url):
        # if not connected
        if not self.bot.voice_clients:
            await self.join_if_summoner_connected(ctx)

        # if muted, refuse to play music
        if ctx.guild.me.voice.mute:
            await ctx.send("I'm server muted. Unmute me before trying to play music.")
            time.sleep(5)
            await self.leave(ctx)
            return

        with yt_dlp.YoutubeDL(YTDLP_OPTS) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                url = info["url"]
            except Exception as e:
                await ctx.send(f"An error occurred while trying to play the video: {e}")
                return

        await ctx.send(embed=YoutubeSong.build_yt_embed(info))
        try:
            self.voice_client.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTS))
        except Exception as e:
            await ctx.send(f"An error occurred while trying to play the audio: {e}")


async def setup(bot):
    await bot.add_cog(Music(bot))
