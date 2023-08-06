from collections import deque
from datetime import timedelta
from functools import partial

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
        volume: float = 0.5,
    ) -> None:
        super().__init__(source, volume=volume)
        self.title = title
        self.url = url
        self.display_url = display_url
        self.requester = requester
        self.uploader_name = uploader_name
        self.uploader_url = uploader_url
        self.duration = duration
        self.thumbnail_url = thumbnail_url

    @classmethod
    def from_url(cls, requested_url: str, requester: str) -> "YoutubeSource":
        """
        Given a youtube url, extract metadata needed to display information
        and play the audio.
        """
        with yt_dlp.YoutubeDL(YTDLP_OPTS) as ydl:
            info = ydl.extract_info(requested_url, download=False)
            if info is None:
                raise Exception("ydl unable to extract info")

        url = info["url"]
        source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTS)

        return cls(
            source=source,
            title=info.get("title", "Title not found"),
            url=url,
            display_url=requested_url,
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
            + f"\nRequested by: {self.requester}",
        )
        embed.set_image(url=self.thumbnail_url)
        return embed

    def __repr__(self):
        return f"**{self.title}** ({self.duration})"


# TODO inactivity timeout
# TODO on event bot muted, if music playing, pause music
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._queue = deque()
        self.voice_client = None

    @commands.command()
    async def leave(self, ctx):
        """
        If the bot is connected, disconnects it from the channel.
        """
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
        else:
            await ctx.send("I'm not connected to a voice channel.")

    @commands.command()
    async def view_queue(self, ctx):
        """
        Prints the queue where the first line is the upcoming song.
        """
        await ctx.send("Queue:\n" + "\n".join(str(x) for x in self._queue))

    @commands.command()
    async def skip(self, ctx):
        """
        Skip the currently playing song.
        """
        if (vc := ctx.voice_client) is not None:
            vc.stop()
        else:
            await ctx.send("Nothing is playing.")

    @commands.command()
    async def play(self, ctx, url):
        """
        Joins the call. Given a url, creates a song and moves it to the start of
        the queue. If a song is currently playing, it will be skipped.
        """
        if not self.bot.voice_clients:
            await self._join_if_summoner_connected(ctx)

        self._queue.insert(0, YoutubeSource.from_url(url, ctx.author.name))
        if self._is_playing():
            await self.skip(ctx)
            await self._play_next(ctx)

    @commands.command()
    async def queue(self, ctx, url) -> None:
        """
        Joins the call. Given a url, creates a song and adds it to the end of
        the queue.
        """
        if not self.bot.voice_clients:
            await self._join_if_summoner_connected(ctx)
        self._queue.append(YoutubeSource.from_url(url, ctx.author.name))

        if not self._is_playing():
            await self._play_next(ctx)

    async def _play_next(self, ctx):
        song = self._queue.popleft()

        if not self.bot.voice_clients:
            await self._join_if_summoner_connected(ctx)

        if self.voice_client:
            await ctx.send(embed=song.build_yt_embed())
            self.voice_client.play(song, after=partial(self._play_next, ctx=ctx))

    async def _join_if_summoner_connected(self, ctx) -> bool:
        if ctx.author.voice:
            self.voice_client = await ctx.author.voice.channel.connect()
            return True
        return False

    def _is_playing(self) -> bool:
        return self.voice_client is not None and self.voice_client.is_playing()


async def setup(bot):
    await bot.add_cog(Music(bot))
