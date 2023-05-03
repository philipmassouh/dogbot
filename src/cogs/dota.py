import warnings
from datetime import date
from pathlib import Path

import discord
import requests
import static_frame as sf
from discord.ext import commands

warnings.filterwarnings("ignore")
import os

import matplotlib.pyplot as plt
import seaborn as sns
from fuzzywuzzy import process

rank_map = {
    "Herald": "1",
    "Guardian": "2",
    "Crusader": "3",
    "Archon": "4",
    "Legend": "5",
    "Ancient": "6",
    "Divine": "7",
    "Immortal": "8",
    "Pro": "pro",
}


class Dota(commands.Cog):
    api_root = "https://api.opendota.com/api/"

    def __init__(self, bot):
        self.bot = bot
        self.heroes = self._get_heroes()

    @classmethod
    def _get_heroes(cls) -> sf.Frame:
        hero_dict = {
            h["localized_name"]: h
            for h in requests.get(cls.api_root + "heroStats").json()
        }
        heroes = sf.FrameGO.from_dict_records_items(hero_dict.items())
        for k, v in rank_map.items():
            heroes[k] = heroes[f"{v}_win"] / heroes[f"{v}_pick"]
        return heroes.to_frame()

    def _fuzzy_match_hero(self, name: str) -> str:
        """
        return the highest probability match of a dota hero given a string
        """
        # TODO consider failing under a threshold
        result = process.extractOne(name, self.heroes.index)
        if result:
            return result[0]
        else:
            raise Exception("no matches")  # TODO

    def _get_winrate(self, hero: str) -> sf.Series:
        return self.heroes[list(rank_map.keys())].loc[hero]

    def _get_winrate_plot(self, data: sf.Series, hero: str) -> Path:
        sns.set_palette(sns.color_palette(["#7289da", "#99aab5"]))
        fig, ax = plt.subplots()
        bars = ax.barh(data.index, data.values)
        ax.axvline(x=data.mean(), color="#ffffff", linestyle="--")

        ax.set_title(f"{hero} winrate", color="#ffffff")
        ax.set_xlabel("Win Rate", color="#ffffff")
        ax.set_ylabel("Rank", color="#ffffff")

        for i, bar in enumerate(bars):
            value = data.iloc[i]
            ax.text(
                bar.get_width() + 0.005,
                bar.get_y() + bar.get_height() / 2,
                f"{value:.1%}",
                ha="left",
                va="center",
                color="#ffffff",
            )

        ax.tick_params(axis="x", colors="#ffffff")
        ax.tick_params(axis="y", colors="#ffffff")
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)

        # fig.patch.set_facecolor("#23272a")
        # ax.patch.set_facecolor("#23272a")
        plt.savefig(fout := f"{hero}_winrate_{date.today()}.png", transparent=True)
        return Path(fout)

    @commands.command("dota_wr")
    async def winrate(self, ctx, *hero):
        hero = " ".join(hero)
        hero = self._fuzzy_match_hero(hero)
        winrate_data = self._get_winrate(hero)
        fp = self._get_winrate_plot(winrate_data, hero)
        with open(fp, "rb") as image:
            await ctx.send(file=discord.File(image, str(fp)))
        os.remove(fp)

    @commands.command("dota_counters")
    async def counters(self, ctx, *hero):
        hero = " ".join(hero)
        hero = self._fuzzy_match_hero(hero)
        hero_id = self.heroes["id"].loc[hero]
        matchups = requests.get(
            f"https://api.opendota.com/api/heroes/{hero_id}/matchups"
        ).json()
        ordered = sorted(
            matchups, key=lambda m: m["wins"] / m["games_played"], reverse=True
        )
        icon_links = [
            "https://api.opendota.com"
            + self.heroes["icon"].loc[self.heroes["id"] == x["hero_id"]].values[0][:-1]
            for x in ordered[:5]
        ]
        for icon in icon_links:
            await ctx.send(icon)


async def setup(bot):
    await bot.add_cog(Dota(bot))
