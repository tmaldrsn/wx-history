import os
import datetime
import sqlite3
import urllib.request
from bs4 import BeautifulSoup


def is_db_path(db_path):
    """Returns whether the specified path is a database"""
    return os.path.splitext(db_path)[-1].lower() == ".db"


def connect_to_db(db_path):
    """Returns a sqlite3 database connection object from a db path"""
    try:
        if not is_db_path(db_path):  # pragma: no cover
            raise Exception("Observations database does not exist!")
        else:
            con = sqlite3.connect(db_path)
            return con
    except:  # pragma: no cover
        raise Exception(
            "Was not able to connect to the observations database."
        )


def get_adjusted_date(day, obs_day, ref_date=None):
    if ref_date == None:
        now_datetime = datetime.datetime.today()
    else:  # pragma: no cover
        now_datetime = ref_date  # for testing purposes only

    most_recent_year = now_datetime.year
    most_recent_month = now_datetime.month
    most_recent_day = day

    if now_datetime.day == 1 and most_recent_day != 1:  # pragma: no cover
        most_recent_month -= 1
        if most_recent_month == 0:
            most_recent_year -= 1
            most_recent_month = 12
    most_recent_date = datetime.date(
        year=most_recent_year,
        month=most_recent_month,
        day=most_recent_day
    )

    if obs_day != most_recent_day:
        most_recent_date -= datetime.timedelta(days=1)
    return most_recent_date.strftime("%m/%d/%Y")


def get_observations_request(station_id, timeout=3):
    """Returns a urllib.request.Request object for the observation page of the station"""
    return urllib.request.urlopen(f"https://w1.weather.gov/data/obhistory/{station_id}.html", timeout=timeout)
