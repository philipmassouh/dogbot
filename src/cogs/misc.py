import random

import discord
from discord.ext import commands


class Misc(commands.Cog):
    # fmt: off
    leet_dict = dict(
        A=['4', '/\\', '[@]', '/-\\', '^', '(L', '[Д]'],
        B=['I3', '8', '13', '|3', '[ß]', '!3', '(3', '/3', ')3', '|-]', 'j3'],
        C=['[', '[¢]', '<', '(', '[©]'],
        D=[')', '|)', '(|', '[)', 'I>', '|>', '?', 'T)', 'I7', 'cl', '|}', '|]'],
        E=['3', '&', '[£]', '[€]', '[-', '|=-'],
        F=['|=', '[ƒ]', '|#', 'ph', '/=', 'v'],
        G=['6', '&', '(_+', '9', 'C-', 'gee', '(?,', '[,', '{,', '<-', '(.'],
        H=['#', '/-/', '\\-\\', '[-]', ')-(', '(-)', ':-:', '|~|', '|-|', ']~[', '}{', '!-!', '1-1', '\\-/', 'I+I', '?'],
        I=['1', '|', '][', '!', 'eye', '3y3'],
        J=[',_|', '_|', '._|', '._]', '_]', ',_]', ']'],
        K=['>|', '|<', '1<', '|c', '|(7<'],
        L=['1', '2', '£', '7', '|_', '|'],
        M=['/\\/\\', '/V\\', '[V]', '|\\/|', '^^', '<\\/>', '{V}', '(v)', '(V)', '|\\|\\', ']\\/[', 'nn', '11'],
        N=['^/', '|\\|', '/\\/', '[\\]', '<\\>', '{\\}', '/V', '^', 'ท', '[И]'],
        O=['0', '()', 'oh', '[]', 'p', '<>', 'Ø'],
        P=['|*', '|o', '|[º]', '?', '|^', '|>', '|"', '9', '[]D', '|[°]', '|7'],
        Q=['(_/)', '()_', '2', '0_', '<|', '&', '9', '[¶]', '⁋', '[℗]'],
        R=['I2', '9', '|`', '|~', '|?', '/2', '|^', 'lz', '7', '2', '12', '[®]', '[z', '[Я]', '.-', '|2', '|3'],
        S=['5', '$', 'z', '[§]', 'ehs', 'es', '2'],
        T=['7', '+', '-|-', '][', '[†]', '«|»', '~|~'],
        U=['(_)', '|_|', 'v', 'L|', 'บ'],
        V=['\\/', '|/', '\\|', '/'],
        W=['\\/\\', 'vv', '\\N', '\'//', '\\\'', '\\^/', '\\/\\', '(n)', '\\V/', '\\X/', '\\|/', '\\_|_/', '\\_:_/', 'uu', '2u', '\\/\\\\//\\\\//', 'พ', '[₩]'],
        X=['><', '}{', 'ecks', '[×]', '[?]', '}{', ')(<', ']['],
        Y=['j', '`/', '\\|/', '[¥]', '\\//'],
        Z=['2', '7_', '-/_', '%', '>_', 's', '~/_', '-\\_', '/', '-|_']
    )
    # fmt: on

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def leetspeak(self, ctx, *, sentence):
        leetspeak_sentence = []
        for char in sentence:
            if char.isalpha():
                uppercase_char = char.upper()
                if uppercase_char in self.leet_dict:
                    leetspeak_sentence.append(
                        random.choice(self.leet_dict[uppercase_char])
                    )
                else:
                    leetspeak_sentence.append(char)
            else:
                leetspeak_sentence.append(char)

        await ctx.send("".join(leetspeak_sentence))

    @commands.command()
    async def uwufy(self, ctx, *, sentence):
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
