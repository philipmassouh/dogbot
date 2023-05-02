from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def uwufy(self, ctx, *sentence):
        # TODO optimize with better rules and regex
        sentence = " ".join(sentence)
        await ctx.send(
            sentence.replace("ing ", "wing").replace("r", "w").replace("l", "w")
            + " teehee"
        )


async def setup(bot):
    await bot.add_cog(Misc(bot))
