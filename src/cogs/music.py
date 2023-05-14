import time
from collections import deque
from datetime import timedelta

import discord
import yt_dlp
from discord.ext import commands

from music_constants import FFMPEG_OPTS, YTDLP_OPTS


class YoutubeSource(discord.PCMVolumeTransformer):
    def __init__(
        self,
        source: discord.FFmpegPCMAudio,
        title: str,
        url: str,
        display_url: str,
        requester: str,
        uploader_name: str,
        uploader_url: str,
        duration: timedelta,
        thumbnail_url: str,
    ) -> None:
        super().__init__(source, volume=0.5)
        self.title = title
        self.url = url
        self.display_url = display_url
        self.requester = requester
        self.uploader_name = uploader_name
        self.uploader_url = uploader_url
        self.duration = duration
        self.thumbnail_url = thumbnail_url

    @classmethod
    def from_url(cls, link: str, requester: str) -> "YoutubeSource":
        """
        Given a youtube url, extract metadata needed to display information
        and play the audio.
        """
        with yt_dlp.YoutubeDL(YTDLP_OPTS) as ydl:
            info = ydl.extract_info(link, download=False)
            if info is None:
                raise Exception("ydl unable to extract info")

        url = info["url"]
        source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTS)

        return cls(
            source=source,
            title=info.get("title", "Title not found"),
            url=url,
            display_url=link,
            requester=requester,
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
            url=self.display_url,
            description="**Now Playing**"
            + f"\nUploader: [{self.uploader_name}]({self.uploader_url})"
            + f"\nDuration: {self.duration}"
            + f"\n Requested by: {self.requester}",
        )
        embed.set_image(url=self.thumbnail_url)
        return embed

    def __repr__(self):
        return f"**{self.title}** ({self.duration})"


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._queue = deque()

    # TODO inactivity timeout

    # TODO on event bot muted, if music playing, pause music

    @commands.command()
    async def leave(self, ctx):
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
        else:
            await ctx.send("I'm not connected to a voice channel.")

    @commands.command()
    async def view_queue(self, ctx):
        await ctx.send("Queue:\n" + "\n".join(str(x) for x in self._queue))

    @commands.command()
    async def skip(self, ctx):
        if (vc := ctx.voice_client) is not None:
            vc.stop()
            await self._play(ctx)
        else:
            await ctx.send("Nothing is playing.")

    @commands.command()
    async def queue(self, ctx, url):
        if not self.bot.voice_clients:
            await self._join_if_summoner_connected(ctx)

        self._queue.append(song := YoutubeSource.from_url(url, ctx.author.name))
        await ctx.send(f"Added to queue: {song}")

    @commands.command()
    async def play(self, ctx, url):
        if not self.bot.voice_clients:
            await self._join_if_summoner_connected(ctx)

        self._queue.appendleft(song := YoutubeSource.from_url(url, ctx.author.name))
        await ctx.send(f"Moving {song} to front of queue and playing.")
        await self.skip(ctx)

    async def _play(self, ctx):
        """
        will play a song and keep playing until queue is empty.
        """
        if len(self._queue) > 0:
            song = self._queue.popleft()

            if self.voice_client is None:
                await ctx.send(f"Bot disconnected. Something's broken.")
                return

            await ctx.send(embed=song.build_yt_embed())
            try:
                self.voice_client.play()
            except Exception as e:
                await ctx.send(f"An error occurred while trying to play the audio: {e}")
            breakpoint()
            await self._play(ctx)

    async def _join_if_summoner_connected(self, ctx) -> bool:
        """
        If summoner in a voice call, join and return True, False otherwise.
        """
        if ctx.author.voice:
            self.voice_client = await ctx.author.voice.channel.connect()
            return True
        return False


async def setup(bot):
    await bot.add_cog(Music(bot))
