
# coding: utf-8

import logging
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn import linear_model
from datetime import timedelta
import database

logging.basicConfig(level=logging.DEBUG)

def raw_to_hum(raw):
    def convert_raw_values(v):
        return (1023 - v) / 10.23
    return raw.resample('1h').mean().reindex().apply(convert_raw_values)


def predict_value(data, target):
    offset = -24
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
    try:
        left = predict_value(data[data[col].notnull()][col], 40).days
    except ValueError:
        return "n/a"
    else:
        if left > 0:
            return "{} days".format(str(left))
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
        label.set_text(time_remaining(data, col))

def status_message(data):
    rv = "Current estimates\n"
    vals = [(plant, time_remaining(data, plant)) for plant in data.columns]
    for plant, rem in sorted(vals, key=lambda tup: tup[1]):
        rv += "  {:<16}{} ({:.2f}%)\n".format(
            database.NAMES[int(plant)], rem, data[plant][-1])

    return rv
    

if __name__ == "__main__":
    # raw = database.read_data_csv("data/HUMINO.CSV")
    raw = database.read_data()
    data = raw_to_hum(raw)
    # logging.info(status_message(data))
    make_plot(data)
    plt.savefig('plot.png')