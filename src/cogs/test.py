import matplotlib.pyplot as plt
import requests
import seaborn as sns
import static_frame as sf

api_root = "https://api.opendota.com/api/"
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
api_root = "https://api.opendota.com/api/"
hero_dict = {h["localized_name"]:h for h in requests.get(api_root + "heroStats").json()}
heroes = sf.FrameGO.from_dict_records_items(hero_dict.items())
for k,v in rank_map.items():
    heroes[k] = heroes[f"{v}_win"]/heroes[f"{v}_pick"]
winrates = heroes[list(rank_map.keys())]

breakpoint()
plt.show()