import warnings
from datetime import date
from pathlib import Path

import discord
import requests
import static_frame as sf
from bs4 import BeautifulSoup
from discord.ext import commands
from PIL import Image

import constants

warnings.filterwarnings("ignore")
import os

import matplotlib.pyplot as plt
import seaborn as sns
from fuzzywuzzy import process


class Dota(commands.Cog):
    api_root = "https://api.opendota.com/api/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    }

    def __init__(self, bot):
        self.bot = bot
        self.heroes = self._from_opendota()

    @classmethod
    def _from_opendota(cls) -> sf.Frame:
        """
        Retrieve hero stats from the opendota api.
        """
        resp = requests.get(cls.api_root + "heroStats")

        heroes = sf.FrameGO.from_dict_records(resp.json())
        heroes = heroes.set_index("id", drop=True)

        # calculate per-rank winrates
        for r in constants.RankMap:
            heroes[f"{r.name}_wr"] = (
                heroes[f"{r.value}_win"] / heroes[f"{r.value}_pick"]
            )

        return heroes.to_frame()

    @classmethod
    def _fuzzy_match_hero(cls, hero_dirty: str) -> int:
        """
        Fuzzymatch user input to a hero name and return the id.
        """
        MATCH_THRESHOLD = 0
        result = process.extractOne(hero_dirty, constants.HERO_TO_ID.keys())

        if result and result[1] > MATCH_THRESHOLD:
            return constants.HERO_TO_ID[result[0]]

        raise Exception(f"No matches for {hero_dirty}")

    def _get_winrate(self, hero_id: int) -> sf.Series:
        """
        Given a hero_id, return the winrates in all ranks.
        """
        winrate_columns = [f"{r.name}_wr" for r in constants.RankMap]
        return self.heroes[winrate_columns].loc[hero_id]

    @classmethod
    def _get_winrate_plot(cls, data: sf.Series, hero: int) -> Path:
        new_labels = [x.removesuffix("_wr") for x in data.index.values]
        data = data.relabel(new_labels)
        fig, ax = plt.subplots()
        bars = ax.barh(data.index, data.values, color="#5865F2")
        mean = data.mean()
        ax.axvline(x=mean, color="#ffffff", linestyle="--")
        ax.text(
            mean,
            ax.get_ylim()[1],
            f"Weighted mean: {mean:.2f}",
            ha="center",
            va="bottom",
            color="white",
        )

        ax.set_title(f"{constants.ID_TO_HERO[hero]} winrate", color="#ffffff")
        ax.set_xlabel("Win Rate", color="#ffffff")
        ax.set_ylabel("Rank", color="#ffffff")

        bar_x = max((bar.get_width() for bar in bars))

        for i, bar in enumerate(bars):
            value = data.iloc[i]
            ax.text(
                bar_x + 0.005,
                bar.get_y() + bar.get_height() / 2,
                f"{value:.1%}",
                ha="left",
                va="center",
                color="#ffffff",
            )

        ax.tick_params(axis="x", colors="#ffffff")
        ax.tick_params(axis="y", colors="#ffffff")
        ax.spines["bottom"].set_color("white")
        ax.spines["top"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.spines["right"].set_color("white")
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.set_xlim([data.min() - 0.1, data.max()])  # type: ignore
        ax.grid(False)

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

    @classmethod
    def _counters_from_dotabuff(cls, hero_id: int) -> list[int]:
        """
        Return a list of hero IDs representing the counters of a given `hero_id`
        """
        hero_for_url = constants.ID_TO_HERO[hero_id].lower()
        soup = BeautifulSoup(
            requests.get(
                f"https://www.dotabuff.com/heroes/{hero_for_url}",
                headers=cls.headers,
            ).content,
            "html",
        )

        if header := soup.find(string="Worst Versus"):
            table = header.find_next("table")
        else:
            raise Exception("'Worst Versus' not found")
        counters = [
            cls._fuzzy_match_hero(
                row.find_all("td")[0]
                .find_next("a")
                .get("href")
                .removeprefix("/heroes/")
            )
            for row in table.find_all("tr")[1:]  # type: ignore
        ]

        return counters

    def _hero_image(self, heroes: list[int], fp: Path) -> None:
        """
        Given a list of hero IDs `heroes`, and an `fp`, return a path
        to a single image of all hero icons concatenated on the x-axis.
        """
        icon_links = (
            "https://api.opendota.com" + partial_url[:-1]
            for partial_url in self.heroes.loc[heroes]["icon"].values
        )

        images = (
            requests.get(url, headers=self.headers, stream=True).raw
            for url in icon_links
        )

        combined = Image.new("RGBA", (32 * len(heroes), 32), (0, 0, 0, 0))
        for i, img in enumerate(images):
            combined.paste(Image.open(img), (i * 32, 0))

        combined.save(fp)

    @commands.command("dota_counters")
    async def counters(self, ctx, *, hero):
        hero_id = self._fuzzy_match_hero(hero)
        counters = self._counters_from_dotabuff(hero_id)

        fp = Path(f"{hero}_counters_{date.today()}.png")
        self._hero_image(counters, fp)

        with open(fp, "rb") as image:
            await ctx.send(file=discord.File(image, str(fp)))
        os.remove(fp)


async def setup(bot):
    await bot.add_cog(Dota(bot))
