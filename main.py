import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError


def set_x_ticks(figure, how_many):
    """ A function that allows as to choose how many x_axis ticks we want to
     see, takes matplotlib figure as an input. When the number of x_tick labels
     does not divide evenly into how_many, there is one less x_tick displayed."""
    ticks = figure.get_xticklabels()
    length = len(ticks)
    n = length // how_many
    for ind, label in enumerate(ticks):
        if ind % n == 0:  # every nth label is kept
            label.set_visible(True)
        else:
            label.set_visible(False)


def scrape_values(url="https://nuforc.org/webreports/ndxevent.html", retries=3):
    """Scrapes values from National UFO Reporting Center, may not work with the url
     variable changed. Number of retries is set to 3 by default. Returns
     dates and counts lists as a length-two tuple"""
    for n in range(retries):
        try:
            data = requests.get(url)
            data.raise_for_status()
        except HTTPError as exc:
            code = exc.response.status_code
            if code in [429, 500, 502, 503, 504]:
                time.sleep(5)
                continue
            raise UserWarning(f'Not able to reach the site with {retries} attempts.')

    soup = BeautifulSoup(data.content, "html.parser")
    dates = [i.get_text() for i in soup.find_all("a")][1:-1]
    counts = np.array([int(i.get_text()) for i in soup.find_all("td")[1::2]][:-1])
    return dates, counts


def make_plot(data, how_many, size=(14, 6.10), x_fontsize=12, y_fontsize=12, title_fontsize=16, y_tick_fontsize=12, x_tick_fontsze=12):
    """ Creates a seaborn plot with customizable fontsizes and number of x_ticks visible."""
    sns.set(rc={'figure.figsize': size})
    sns.set_style("ticks")
    fig = sns.barplot(x="Dates", y="Counts", data=data)
    fig.set_xlabel("Dates", fontsize=x_fontsize)
    fig.set_ylabel("Count", fontsize=y_fontsize)
    fig.set_title(label="Number of UFO sightings reported monthly since 2005", fontsize=title_fontsize)
    fig.invert_xaxis()
    sns.despine(trim=True)
    fig.set_yticklabels(fig.get_yticks(), size=y_tick_fontsize)
    _, xlabels = plt.xticks()
    fig.set_xticklabels(xlabels, size=x_tick_fontsze)
    set_x_ticks(figure=fig, how_many=how_many)
    plt.tight_layout()
    plt.show()


def main():
    dates, counts = scrape_values()
    num_of_months = 200  # Number of months we want to consider, may be changed up to 900
    df = pd.DataFrame(data={"Dates": dates, "Counts": counts}).iloc[:num_of_months]
    df['Dates'] = pd.to_datetime(df['Dates']).dt.strftime('%Y-%m')  # Changing ['Date'] column type to a datetime object
    make_plot(data=df, how_many=13)


if __name__ == "__main__":
    main()
