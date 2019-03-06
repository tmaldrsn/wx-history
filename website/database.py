import os
import datetime
import urllib.request
from bs4 import BeautifulSoup

import sqlite3


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
