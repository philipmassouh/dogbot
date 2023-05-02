import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import static_frame as sf
from enum import Enum, auto
from typing import NamedTuple
data = pd.Series({
    'herald_wr': 0.532317,
    'guardian_wr': 0.533991,
    'crusader_wr': 0.526788,
    'archon_wr': 0.522019,
    'legend_wr': 0.515731,
    'ancient_wr': 0.515258,
    'divine_wr': 0.508929,
    'immortal_wr': 0.499346,
    'pro_wr': 0.478571
})

colors = sns.color_palette(['#7289da', '#99aab5'])

sns.set_palette(colors)

fig, ax = plt.subplots()
bars = ax.barh(data.index, data.values)

mean = data.mean()
ax.axvline(x=mean, color='#ffffff', linestyle='--')

ax.set_title('Axe winrate',color='#ffffff')
ax.set_xlabel('Win Rate',color='#ffffff')
ax.set_ylabel('Rank',color='#ffffff')

for i, bar in enumerate(bars):
    value = data.iloc[i]
    ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height() / 2, f'{value:.1%}', ha='left', va='center', color='#ffffff')

ax.tick_params(axis='x', colors='#ffffff')
ax.tick_params(axis='y', colors='#ffffff')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

fig.patch.set_facecolor('#23272a')
ax.patch.set_facecolor('#23272a')

plt.savefig('win_rates.png', transparent=True)

plt.show()

class DarkPalette(NamedTuple):
    background = 

class LightPalette(NamedTuple):
    background = #ffffff

def get_winrate_plot(self, data: sf.Series) -> plt:
