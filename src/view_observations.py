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

fileConfig('logging_config.ini')
logger = logging.getLogger()
DB = "observations.db"
STATION = "KTOL"
ITEM = "Air Temperature"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        STATION = str(sys.argv[1])
    else:
        logger.info(
            "No station was given as an argument, using KTOL by default.")
        STATION = "KTOL"

    try:
        con = sqlite3.connect(DB)
    except:
        raise Exception(f"Was not able to connect to observations database")

    query = f"""select * from {STATION} order by date, time"""
    df = pd.read_sql_query(query, con)

    plt.figure()
    plt.title(f"{ITEM} for {STATION}")
    plt.xlabel("Date")
    plt.ylabel(f"{ITEM}")

    plt.plot_date([datetime.datetime.strptime('{} {}'.format(df["Date"][i], df["Time"][i]), '%m/%d/%Y %H:%M')
                   for i in range(len(df["Date"]))], list(map(int, df[ITEM])), fmt="r-", xdate=True, ydate=False)
    plt.show()
