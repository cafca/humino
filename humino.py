
# coding: utf-8

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn import linear_model
from datetime import timedelta


def raw_to_hum(raw):
    def convert_raw_values(v):
        return (1023 - v) / 10.23
    return raw.resample('1h').mean().reindex().apply(convert_raw_values)


def predict_value(data, target):
    offset = -24
    step_width = 5

    y = data.values.reshape(-1, 1)[offset:]
    x = ((data.index -  data.index[offset]) / 300000000000)[offset:].values.reshape(-1, 1).astype('int')

    regr = linear_model.LinearRegression()
    regr.fit(x, y)
    
    rem = -1 * step_width * ((y[-1] - target) / regr.coef_[0])[0]
    return timedelta(minutes=rem)
    
    
#for col in data.columns:
#    print(col, predict_value(data[data[col].notnull()][col], 50).days, 'days')

def make_plot(data):
    data_selection = data[-(5 * 24):]

    date_format = mdates.DateFormatter('%m-%d')
    date_hours_format = mdates.DateFormatter('%m-%d\n%H:%M')

    sns.set()
    fig1, ax1 = plt.subplots()
    # the size of A4 paper
    fig1.set_size_inches(11.7, 8.27)
    ax1.xaxis.set_major_formatter(date_format)
    ax1 = sns.lineplot(data=data_selection, linewidth=2.5, ax=ax1, dashes=False)

    legend = ax1.legend()
    for i, col in enumerate(data.columns):
        left = predict_value(data[data[col].notnull()][col], 40).days
        label = legend.get_texts()[i]
        if left > 0:
            label.set_text("{} days".format(str(left))
        else:
            label.set_text("wet")
    

if __name__ == "__main__":
    raw = pd.read_csv('data/HUMINO.csv', 
                    index_col=0, 
                    parse_dates=True)

    data = raw_to_hum(raw)
    make_plot(data)
    plt.savefig('plot.png')