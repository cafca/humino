
# coding: utf-8

import logging
import os
from datetime import datetime, timedelta
from operator import itemgetter

# Tell Matplotlib not to use GTK before importing pyplot on Raspberry
if os.uname()[4].startswith('arm'):
    import matplotlib
    matplotlib.use('Agg')

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pdhumino
import seaborn as sns

import config
import database

logging.basicConfig(level=logging.INFO)


def raw_to_hum(raw):
    def convert_raw_values(v):
        return (1023 - v) / 10.23
    return raw \
        .resample('{}min'.format(config.STEP)).mean() \
        .reindex(method='nearest') \
        .apply(convert_raw_values)


def make_plot(data):
    if data.empty:
        raise ValueError("The dataset is empty")

    date_format = mdates.DateFormatter('%m-%d')
    # date_format = mdates.DateFormatter('%m-%d\n%H:%M')

    sns.set()
    fig1, ax1 = plt.subplots()
    # the size of A4 paper
    fig1.set_size_inches(11.7, 8.27)
    ax1.xaxis.set_major_formatter(date_format)
    ax1 = sns.lineplot(data=data, linewidth=2.5, ax=ax1, dashes=False)

    legend = ax1.legend()
    for i, col in enumerate(data.columns):
        label = legend.get_texts()[i]
        label.set_text(config.PLANTS[col][0])


def status_message(data):
    rv = datetime.now().strftime("%d.%m. %H:%M")
    rv += "\n\n"

    if data.empty:
        rv += "There are no recorded measurements in the last 7 days"
        return rv

    def getProgress(plant):
        current = data[plant][-1]
        low = config.PLANTS[int(plant)][1]
        high = 80.0
        try:
            rv = int(100.0 * (current - low) / (high - low))
        except ValueError:
            rv = 0
        return rv

    values = [(plant, getProgress(plant))
              for plant in data.columns if not np.isnan(data[plant][-1])]

    for plant, progress in sorted(values, key=itemgetter(1)):
        threshold = config.PLANTS[int(plant)][1]
        current_value = data[plant][-1]
        status = "🍂" if progress <= 0 else "🍃" if progress <= 10 else "🌱"
        rv += "{status} {progress:2d}% {name}\n".format(
            status=status,
            progress=progress if progress >= 0 else 0,
            name=config.PLANTS[int(plant)][0]
        )

    return rv


if __name__ == "__main__":
    # For reading from csv:
    # raw = database.read_data_csv("data/HUMINO.CSV")
    raw = database.read_data()

    data = raw_to_hum(raw)
    status = status_message(data)
    with open(os.path.join(config.OUT_FOLDER, "status.txt"), "w") as f:
        f.write(status)

    logging.info(status)

    try:
        make_plot(data)
    except ValueError as e:
        logging.error("Error making plot: {}".format(e))
    else:
        plt.savefig(os.path.join(config.OUT_FOLDER, 'plot.png'))
