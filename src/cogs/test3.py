import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pandas as pd

# Create the DataFrame
data = {
    'Rank': ['Herald', 'Guardian', 'Crusader', 'Archon', 'Legend', 'Ancient', 'Divine', 'Immortal', 'Pro'],
    'Win Rate': [0.532317, 0.533991, 0.526788, 0.522019, 0.515731, 0.515258, 0.508929, 0.499346, 0.478571]
}
df = pd.DataFrame(data)

# Load the icons
herald_icon = mpimg.imread('a.png')
guardian_icon = mpimg.imread('a.png')
crusader_icon = mpimg.imread('a.png')
archon_icon = mpimg.imread('a.png')
legend_icon = mpimg.imread('a.png')
ancient_icon = mpimg.imread('a.png')
divine_icon = mpimg.imread('a.png')
immortal_icon = mpimg.imread('a.png')
pro_icon = mpimg.imread('a.png')

# Create the figure and subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

# Plot the icons in the left subplot
ax1.imshow([herald_icon, guardian_icon, crusader_icon, archon_icon, legend_icon, ancient_icon, divine_icon, immortal_icon, pro_icon], aspect='auto')
ax1.axis('off')

# Plot the bar chart in the right subplot
ax2.barh(df['Rank'], df['Win Rate'], color='#7289da', alpha=0.8, height=0.8)
ax2.axvline(df['Win Rate'].mean(), color='red', linestyle='dashed', linewidth=1)
ax2.set_xlim(0.4, 0.6)
ax2.set_xlabel('Win Rate')
ax2.set_ylabel('Rank')

# Set the overall title of the figure
fig.suptitle('Win Rates by Rank')

# Show the plot
plt.show()