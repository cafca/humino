
# coding: utf-8

import os
import logging
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn import linear_model
from datetime import timedelta, datetime
import database
import config

logging.basicConfig(level=logging.DEBUG)

def raw_to_hum(raw):
    def convert_raw_values(v):
        return (1023 - v) / 10.23
    return raw.resample('15min').mean().reindex(method='nearest').apply(convert_raw_values)


def predict_value(data, target):
    offset = -12 * 4  # should come out as 24h when multiplied with resample val
    step_width = 5

    if len(data.index) < -1 * offset:
        raise ValueError("Not enough data to predict")

    y = data.values.reshape(-1, 1)[offset:]
    index_from_offset = data.index -  data.index[offset]
    x = (index_from_offset / 300000000000)[offset:] \
        .values.reshape(-1, 1).astype('int')

    regr = linear_model.LinearRegression()
    regr.fit(x, y)
    
    rem = -1 * step_width * ((y[-1] - target) / regr.coef_[0])[0]
    return timedelta(minutes=rem)

def time_remaining(data, col):
    target = config.PLANTS[col][1]
    try:
        left = predict_value(data[data[col].notnull()][col], target).days
    except ValueError:
        return "n/a"
    else:
        if left > 0:
            return "{} days".format(str(left))
        elif data[col].iloc[-1] <= target:
            return "dry"
        else:
            return "wet"
    
    
#for col in data.columns:
#    print(col, predict_value(data[data[col].notnull()][col], 50).days, 'days')

def make_plot(data):
    date_format = mdates.DateFormatter('%m-%d')
    date_format = mdates.DateFormatter('%m-%d\n%H:%M')

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
    vals = [(plant, time_remaining(data, plant)) for plant in data.columns]
    for plant, rem in sorted(vals, key=lambda tup: tup[1]):
        rv += "  {:<16}{} ({:.2f}%)\n".format(
            config.PLANTS[int(plant)][0], rem, data[plant][-1])

    return rv
    

if __name__ == "__main__":
    # raw = database.read_data_csv("data/HUMINO.CSV")
    raw = database.read_data()
    data = raw_to_hum(raw)
    status = status_message(data)
    with open(os.path.join(config.OUT_FOLDER, "status.txt"), "w") as f:
        f.write(status)
    logging.info(status)
    make_plot(data)
    plt.savefig(os.path.join(config.OUT_FOLDER, 'plot.png'))