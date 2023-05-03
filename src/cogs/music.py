import discord
import yt_dlp as youtube_dl
from discord.ext import commands


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
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

    @commands.command()
    async def play(self, ctx, url):
        if not self.voice_client:
            await ctx.send(
                "I'm not connected to a voice channel. Use the `join` command to summon me to a voice channel."
            )
            return

        # Set up the options for youtube_dl
        ydl_opts = {
            "format": "bestaudio",
            "extractaudio": True,
            "audioformat": "mp3",
            "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
            "restrictfilenames": True,
            "noplaylist": True,
            "nocheckcertificate": True,
            "ignoreerrors": False,
            "logtostderr": False,
            "quiet": True,
            "no_warnings": True,
            "default_search": "auto",
            "source_address": "0.0.0.0",
        }

        FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                url = info["url"]
            except Exception as e:
                await ctx.send(f"An error occurred while trying to play the video: {e}")
                return

        # Play the audio
        try:
            self.voice_client.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS))
            await ctx.send("Playing audio.")
        except Exception as e:
            await ctx.send(f"An error occurred while trying to play the audio: {e}")


async def setup(bot):
    await bot.add_cog(Music(bot))
