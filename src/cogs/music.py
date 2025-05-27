from __future__ import annotations
import asyncio
from collections import deque
from datetime import timedelta
from loguru import logger
import discord
import yt_dlp
from discord.ext import commands, tasks

class YTDLPException(Exception): ...

YTDLP_OPTS = {
    "format": "bestaudio[ext=m4a]/bestaudio/best",
    "quiet": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",
}

FFMPEG_OPTS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

CONSTANT_YTDLP_TITLE = "title"
CONSTANT_YTDLP_URL = "url"
CONSTANT_YTDLP_UPLOADER = "uploader"
CONSTANT_YTDLP_UPLOADER_URL = "uploader_url"
CONSTANT_YTDLP_DURATION = "duration"
CONSTANT_YTDLP_THUMBNAILS = "thumbnails"

discord.opus.load_opus('/opt/homebrew/lib/libopus.dylib')  # or path to opus.dll on Windows


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
    def from_url(cls, requested_url: str, requester: str) -> YoutubeSource:
        logger.info(f"Extracting {requested_url=} from {requester=}")
        with yt_dlp.YoutubeDL(YTDLP_OPTS) as ydl:
            info = ydl.extract_info(requested_url, download=False)
            if info is None:
                logger.error(f"Failed to extract info: {requested_url=}")
                raise YTDLPException()

        title = info.get(CONSTANT_YTDLP_TITLE, "Title not found")
        url = info[CONSTANT_YTDLP_URL]
        uploader = info.get(CONSTANT_YTDLP_UPLOADER, "Uploader not found")
        uploader_url=info.get(CONSTANT_YTDLP_UPLOADER_URL, "Uploader not found")
        duration_seconds = info.get(CONSTANT_YTDLP_DURATION, "Duration not found")
        duration = timedelta(seconds=float(duration_seconds))
        thumbnail_urls = info.get(CONSTANT_YTDLP_THUMBNAILS, [None,])
        thumbnail_url = max(thumbnail_urls, key=lambda t: (t.get("width", 0), t.get("height", 0)))[CONSTANT_YTDLP_URL]

        source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTS)
        logger.info(f"Created source ({title=}, {uploader=})")

        return cls(
            source=source,
            title=title,
            url=url,
            display_url=requested_url,
            requester=requester,
            uploader_name=uploader,
            uploader_url=uploader_url,
            duration=duration,
            thumbnail_url=thumbnail_url,
        )



    @classmethod
    def from_query(cls, url_or_query: str, requester: str) -> "YoutubeSource":
        with yt_dlp.YoutubeDL(YTDLP_OPTS) as ydl:
            if url_or_query.startswith("http://") or url_or_query.startswith("https://"):
                url = url_or_query
            else:
                search_results = ydl.extract_info(f"ytsearch:{url_or_query} lyric", download=False)
                if not search_results or "entries" not in search_results or len(search_results["entries"]) == 0:
                    raise Exception(f"No search results found on YouTube for: {url_or_query}")
                url = search_results["entries"][0]["webpage_url"]

        return cls.from_url(url, requester)



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
        self.last_ctx = None
        self.music_loop.start()
        self.voice_client = None

    @tasks.loop(seconds=1)
    async def music_loop(self):
        if self._is_playing() or len(self._queue) == 0:
            await asyncio.sleep(1)
        else:
            song = self._queue.popleft()
            await self._play(self.last_ctx, song)

    @music_loop.before_loop
    async def before_music_loop(self):
        await self.bot.wait_until_ready()

    @commands.command()
    async def skip(self, ctx):
        """
        Skip the currently playing item.
        """
        self.last_ctx = ctx
        if (vc := ctx.voice_client) is not None:
            vc.stop()
        else:
            await ctx.send("Nothing is playing.")

    @commands.command()
    async def play(self, ctx, *, query):
        """
        Joins the call. Given a url, creates a song and moves it to the front of
        the queue. If a song is currently playing, it will be skipped.
        """
        self.last_ctx = ctx
        if not self.bot.voice_clients:
            await self._join_if_summoner_connected(ctx)

        self._queue.insert(0, YoutubeSource.from_query(query, ctx.author.name))
        if self._is_playing():
            await self.skip(ctx)

    @commands.command()
    async def queue(self, ctx, *, query) -> None:
        """
        Joins the call. Given a url, creates a song and adds it to the back of
        the queue.
        """

        self.last_ctx = ctx
        if not self.bot.voice_clients:
            await self._join_if_summoner_connected(ctx)
        self._queue.append(YoutubeSource.from_query(query, ctx.author.name))

    @commands.command()
    async def view_queue(self, ctx):
        """
        Prints the queue where the first line is the upcoming song.
        """
        self.last_ctx = ctx
        await ctx.send("Queue:\n" + "\n".join(str(x) for x in self._queue))

    @commands.command()
    async def leave(self, ctx):
        """
        If the bot is connected, disconnects it from the channel.
        """
        self.last_ctx = ctx
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
        else:
            await ctx.send("I'm not connected to a voice channel.")

    async def _join_if_summoner_connected(self, ctx) -> bool:
        if ctx.author.voice:
            self.voice_client = await ctx.author.voice.channel.connect()
            return True
        return False

    async def _play(self, ctx, song):
        self.last_ctx = ctx

        if not self.bot.voice_clients:
            await self._join_if_summoner_connected(ctx)

        if self.voice_client:
            await ctx.send(embed=song.build_yt_embed())
            self.voice_client.play(song)

    def _is_playing(self) -> bool:
        return self.voice_client is not None and self.voice_client.is_playing()


async def setup(bot):
    await bot.add_cog(Music(bot))
