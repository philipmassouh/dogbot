from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def uwufy(self, ctx, sentence):
        await ctx.send(sentence.replace("r", "w").replace("l", "w") + "teehee")


async def setup(bot):
    await bot.add_cog(Misc(bot))
