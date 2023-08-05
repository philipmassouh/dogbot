import warnings

import requests

warnings.filterwarnings("ignore")
import typing as tp

from fuzzywuzzy import process

ROOT = "https://api.opendota.com/api/"

heroes = {h["localized_name"]: h for h in requests.get(ROOT + "heroStats").json()}

fuzzy_match_hero = lambda raw_in: process.extractOne(raw_in, heroes.keys())[0]
hero_wr = lambda hero: heroes[hero]["turbo_wins"] / heroes[hero]["turbo_picks"]

radiant_picks = list(
    map(fuzzy_match_hero, input("radiant heroes comma separated: ").split(","))
)
dire_picks = list(
    map(fuzzy_match_hero, input("dire heroes comma separated: ").split(","))
)

radiant = {name: hero_wr(name) for name in radiant_picks}
dire = {name: hero_wr(name) for name in dire_picks}

print("_" * 10)
print("\n".join(map(str, list(radiant.items()))))
print("_" * 10)
print("\n".join(map(str, list(dire.items()))))

print("_" * 10)
print(f"radiant: {sum(radiant.values())/len(radiant.values())}")
print(f"dire: {sum(dire.values())/len(dire.values())}")
