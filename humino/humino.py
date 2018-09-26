
# coding: utf-8

import logging
import os
from datetime import datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn import linear_model

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


def predict_value(data, target):
    # should come out as 24h when multiplied with resample val
    offset = int(-24 * (60 / config.STEP))

    if len(data.index) < -1 * offset:
        raise ValueError("Not enough data to predict")

    y = data.values.reshape(-1, 1)[offset:]
    index_from_offset = data.index - data.index[offset]

    x = (index_from_offset / (config.STEP * 60 * 1000 * 1000 * 1000))[offset:] \
        .values.reshape(-1, 1).astype('int')

    regr = linear_model.LinearRegression()
    regr.fit(x, y)

    rem = -1 * config.STEP * ((y[-1] - target) / regr.coef_[0])[0]
    return timedelta(minutes=rem)


def time_remaining(data, plant):
    target = config.PLANTS[plant][1]
    try:
        left = predict_value(data[data[plant].notnull()][plant], target).days
    except ValueError:
        left = -1
        msg = "n/a"
    else:
        if left > 0:
            msg = "{} days".format(str(left))
        elif data[plant].iloc[-1] <= target:
            msg = "dry"
        else:
            msg = "wet"

    return (plant, left, msg)


def make_plot(data):
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
    rv = "Current estimates\n"
    rv += datetime.now().strftime("%m-%d %H:%M")
    rv += "\n\n"
    vals = [time_remaining(data, plant) for plant in data.columns]
    for plant, val, rem in sorted(vals, key=lambda tup: tup[1]):
        status = "🌱" if data[plant][-1] >= config.PLANTS[int(
            plant)][0] else "🍂"
        rv += "{}  {:<16}{} ({:.2f}%)\n".format(
            status,
            config.PLANTS[int(plant)][0],
            rem,
            data[plant][-1])

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
    make_plot(data)
    plt.savefig(os.path.join(config.OUT_FOLDER, 'plot.png'))
