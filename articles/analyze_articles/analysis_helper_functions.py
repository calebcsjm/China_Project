
# Calculations

def get_articles_per_quarter(df):
    articles_per_quarter = {}

    for quarter in df['year_quarter'].unique():
        articles_per_quarter[quarter] = len(df[df['year_quarter'] == quarter])

    articles_per_quarter = dict(sorted(articles_per_quarter.items()))
    return articles_per_quarter

# Graphing

import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText

def add_correlation_box(series1, series2, ax):
    correlation = round(series1.corr(series2), 2)

    text_box = AnchoredText(f"corr = {correlation}", frameon=True, loc='lower right', pad=0.5)
    plt.setp(text_box.patch, facecolor='white', alpha=0.5)
    ax.add_artist(text_box)

