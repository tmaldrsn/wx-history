import os
import sqlite3
import urllib.request
from bs4 import BeautifulSoup


def is_db_path(db_path):
    """Returns whether the specified path is a database"""
    return os.path.splitext(db_path)[-1].lower() == ".db"


def get_db_connection(db_path):
    """Returns a sqlite3 connection object"""
    return sqlite3.connect(db_path)


def get_db_cursor(db_path):
    """Returns a sqlite3 cursor object given a path to a database"""
    return sqlite3.connect(db_path).cursor()


def get_observations_request(station_id):
    """Returns a urllib.request.Request object for the observation page of the station"""
    return urllib.request.urlopen(f"https://w1.weather.gov/data/obhistory/{station_id}.html")


def get_observations_html(request):
    """Returns the BeautifulSoup object"""
    return BeautifulSoup(request, 'html.parser')
