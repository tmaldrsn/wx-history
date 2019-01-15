import os
import datetime
import sqlite3
import urllib.request
from bs4 import BeautifulSoup


def is_db_path(db_path):
    """Returns whether the specified path is a database"""
    return os.path.splitext(db_path)[-1].lower() == ".db"


def get_db_cursor(db_path):
    """Returns a sqlite3 cursor object given a path to a database"""
    return sqlite3.connect(db_path).cursor()


def get_observations_request(station_id, timeout=3):
    """Returns a urllib.request.Request object for the observation page of the station"""
    return urllib.request.urlopen(f"https://w1.weather.gov/data/obhistory/{station_id}.html", timeout=timeout)


def get_datetime_string(day, time=None):
    """Returns the formatted string for the day and time input"""
    if time:
        return datetime.datetime.today().strftime(f"%m/{day}/%Y {time}")
    return datetime.datetime.today().strftime(f"%m/{day}/%Y")


def get_datetime(date_string, include_time=False):
    """Returns the datetime object for the given string in appropriate format"""
    if include_time:
        return datetime.datetime.strptime(date_string, "%m/%d/%Y %H:%M")
    return datetime.datetime.strptime(date_string, "%m/%d/%Y")
