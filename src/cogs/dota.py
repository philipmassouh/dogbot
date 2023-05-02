import warnings

import requests
import static_frame as sf

# from discord.ext import commands

warnings.filterwarnings("ignore")
from fuzzywuzzy import process

rank_map = {
    "herald_wr":"1",
    "guardian_wr":"2",
    "crusader_wr":"3",
    "archon_wr":"4",
    "legend_wr":"5",
    "ancient_wr":"6",
    "divine_wr":"7",
    "immortal_wr":"8",
    "pro_wr":"pro",
}

class Dota(commands.Cog):
    api_root = "https://api.opendota.com/api/"

    def __init__(self, bot):
        self.bot = bot
        self.heroes = self._get_heroes(self)

    def _get_heroes(self) -> sf.Frame:
        hero_dict = {h["localized_name"]:h for h in requests.get(self.api_root + "heroStats").json()}
        heroes = sf.FrameGO.from_dict_records_items(hero_dict.items())
        for k,v in rank_map.items():
            heroes[k] = heroes[f"{v}_win"]/heroes[f"{v}_pick"]
        return heroes

    def _fuzzy_match_hero(self, name: str) -> str:
        """
        return the highest probability match of a dota hero given a string
        """
        #TODO consider failing under a threshold
        return process.extractOne(name, self.heroes.keys())[0]
    
    #TODO get counters
    
    @commands.command("dota winrate")
    async def winrate(self, ctx):
        if ctx.author.voice:
            self.voice_client = await ctx.author.voice.channel.connect()
        else:
            await ctx.send("You must be in a voice channel to summon me.")


async def setup(bot):
    await bot.add_cog(Dota(bot))
