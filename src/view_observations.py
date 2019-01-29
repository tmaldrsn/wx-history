import os
import sys
import datetime
import sqlite3
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import tabulate
import logging
from logging.config import fileConfig
from src.connect import is_db_path, connect_to_db

fileConfig('logging_config.ini')
logger = logging.getLogger()
DB = "observations.db"
STATION = "KTOL"
ITEM = "Air Temperature"


def get_datetimes_list(df):
    strings = [date + time for date, time in zip(df["Date"], df["Time"])]
    objects = [datetime.datetime.strptime(d, "%m/%d/%Y%H:%M") for d in strings]
    return objects


def generate_plot(db=DB, stations=[STATION], params=[ITEM], output="png"):
    con = connect_to_db(DB)

    query = f"""select * from {STATION} order by substr(date, 7, 4), substr(date, 1, 2), substr(date, 4, 2), time"""
    df = pd.read_sql_query(query, con)

    plt.figure(1)
    plt.title(f"{' '.join(params)} for {STATION}")
    plt.xlabel("Date")
    plt.ylabel(f"{' '.join(params)}")

    obs_datetimes = [date + time for date, time in zip(df["Date"], df["Time"])]
    datetimes = [datetime.datetime.strptime(
        d, "%m/%d/%Y%H:%M") for d in obs_datetimes]

    plt.plot(datetimes, list(map(int, df[ITEM])))
    if output == "png":
        plt.savefig(f"{STATION}-{ITEM}.png")
    plt.show()


def generate_plot_html_element(img_url):
    if img_url[-3:] != "png":
        raise Exception("Not a valid plot image url...")
    return f'''
        <div>
        <img src="{img_url}"></img>
        </div>
    '''


if __name__ == "__main__":
    generate_plot()
