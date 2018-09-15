# coding: utf-8

import logging
import sqlite3
import pandas as pd
import numpy as np

DB_FILENAME = "../data/db.sqlite"

NAMES = [
    'Hibiskus',
    'Walnuss',
    'Blattpflanz',
    'Blattpflanz-2'
]

def init_db():
    logging.info("Init db..")
    conn = sqlite3.connect(DB_FILENAME)
    c = conn.cursor()
    CREATE_TABLES = '''CREATE TABLE humidity (
        id INTEGER PRIMARY KEY NOT NULL,
        plant INTEGER NOT NULL,
        value INTEGER,
        dt VARCHAR(50) NOT NULL
    );'''
    c.execute(CREATE_TABLES)
    conn.commit()
    conn.close()
    
def import_csv(fn):
    raw = pd.read_csv(fn, index_col=0, parse_dates=True)

    print("Reading csv..")
    values = []
    for i in range(len(raw)):
        measurement = raw.iloc[i]
        dt = measurement.name
        for plant_id, col in enumerate(raw.columns):
            values.append((
                plant_id,
                int(measurement[col]) if not np.isnan(measurement[col]) else None,
                dt.isoformat()
            ))
        if i % 10000 == 0: print("{} / {}".format(i, len(raw)))

    print("Importing {} values".format(len(values)))

    conn = sqlite3.connect(DB_FILENAME)
    c = conn.cursor()

    INSERT_VALUES = "INSERT INTO humidity(plant, value, dt) VALUES (?, ?, ?)"
    c.executemany(INSERT_VALUES, values)
    conn.commit()
    conn.close()


def read_data():
    conn = sqlite3.connect(DB_FILENAME)
    data = pd.read_sql_query("SELECT * FROM humidity;", conn)
    conn.close()
    data = data.pivot(index='dt', columns='plant', values='value')
    data.index = pd.to_datetime(data.index)
    return data

def read_data_csv(fn):
    return pd.read_csv(fn, index_col=0, parse_dates=True)

def store_measurements(plant, value, dt):
    conn = sqlite3.connect(DB_FILENAME)
    c = conn.cursor()
    INSERT = "INSERT INTO humidity(plant, value, dt) VALUES (?, ?, ?)"
    rv = c.execute(INSERT, [plant, value, dt])
    conn.close()
    return rv

# if __name__ == '__main__':
#     init_db()
#     import_csv("../data/HUMINO.CSV")