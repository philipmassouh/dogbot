import discord
from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def uwufy(self, ctx, *, sentence):
        # TODO optimize with better rules and regex
        await ctx.send(
            sentence.replace("ing ", "wing").replace("r", "w").replace("l", "w")
            + " teehee"
        )

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite) -> None:
        name = "SOMEONE"
        if invite and invite.inviter and invite.inviter.name:
            name = invite.inviter.name
        message = f"@here ALERT {name} HAS CREATED AN INVITE -- BRACE FOR CRINGE"
        channel = await self.bot.fetch_channel(559158696635269152)
        await channel.send(message)


async def setup(bot):
    await bot.add_cog(Misc(bot))
