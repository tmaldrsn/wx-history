import sqlite3
import os
import sys
import random
import time
import datetime
import urllib.request
from urllib.error import URLError
import logging
from logging.config import fileConfig
from website.database import (
    is_db_path,
    connect_to_db,
)
from bs4 import BeautifulSoup

fileConfig('logging_config.ini')
logger = logging.getLogger()

DB_PATH = "observations.db"
forecast_elements = [
    "Datetime",
    "Wind",
    "Visibility",
    "Weather",
    "Sky Condition",
    "Air Temperature",
    "Dew Point",
    "6HR Max",
    "6HR Min",
    "Humidity",
    "Wind Chill",
    "Heat Index",
    "Altimeter Pressure",
    "Sea Level Pressure",
    "1HR Precip",
    "3HR Precip",
    "6HR Precip"
]


def get_observations_request(station, timeout=3):
    """Returns a urllib.request.Request object for the observation page of the station"""
    return urllib.request.urlopen(f"https://w1.weather.gov/data/obhistory/{station}.html", timeout=timeout)


def create_station_table(cur, station):
    try:
        obs_cols = ','.join('"{}"'.format(w) for w in forecast_elements)
        cur.execute(
            f"""create table if not exists {station} ({obs_cols}, constraint unq unique (date, time))""")
    except sqlite3.OperationalError:  # pragma: no cover
        logger.info(f"Table not created for {station}")


def get_raw_data(station):
    """
    Retrieves raw data from three-day historical table for given station
    """
    # Check if station data request times out
    try:
        req = get_observations_request(station)
        soup = BeautifulSoup(req, 'html.parser')
    except (OSError, URLError):
        logger.warning(f"Station {station} request timed out!!")
        return [], "TO"

    # Extract data and return NA if not available
    try:
        forecast_table = soup.find_all('table')[3]
        forecast_rows = forecast_table.find_all('tr')[3:-3]
    except IndexError:  # pragma: no cover
        logger.warning(f"Station {station} data not available.")
        return [], "NA"
    else:  # pragma: no cover
        if not forecast_rows:
            logger.warning(f"Station {station} data not available.")
            return [], "NA"

    data_rows = [[val.string for val in row.find_all(
        'td')] for row in forecast_rows]
    # Check for completeness of data, return I for incomplete if needed
    if len(data_rows) < 30:
        return data_rows, "I"

    return data_rows, "G"


def get_initial_date(day):
    """
    Given a day-only date, retrieve appropriate date for initial observation

    CAUTION: date is given as a string!!
    """
    date_obj = datetime.date.today()
    if date_obj.day == int(day):
        return date_obj
    elif (date_obj - datetime.timedelta(days=1)).day == int(day):
        date_obj -= datetime.timedelta(days=1)
        return date_obj
    else:
        raise Exception(
            "The date does not match the date of today or yesterday.")


def convert(data, type_cast):
    if data == "NA" or data is None:
        return None
    if data is not None:
        if data[-1] == "%":
            return type_cast(data[:-1])
        return type_cast(data)


def format_rows(data):
    """
    Converts a given array of raw data to appropriate format for historical use
    """
    init_date = get_initial_date(data[0][0])
    # Date formatting
    for row in data:
        # Convert day-only date column and time column to a single datetime with a full date
        if init_date.day != int(row[0]):
            init_date -= datetime.timedelta(days=1)

        obs_datetime = datetime.datetime.combine(
            init_date, datetime.time(int(row[1][:2]), int(row[1][3:])))
        del row[:2]
        row.insert(0, obs_datetime)

        row[1] = convert(row[1], str)        # Wind -> string
        row[2] = convert(row[2], float)      # Vis -> float
        row[3] = convert(row[3], str)        # Weather -> string
        row[4] = convert(row[4], str)        # Sky Condition -> string
        row[5] = convert(row[5], int)        # Air Temp -> integer
        row[6] = convert(row[6], int)        # Dew Point -> integer
        row[7] = convert(row[7], int)        # 6HR Max -> integer or null
        row[8] = convert(row[8], int)        # 6HR Min -> integer or null
        row[9] = convert(row[9], int)        # Humidity -> integer (ignore %)
        row[10] = convert(row[10], int)      # Wind Chill -> integer or null
        row[11] = convert(row[11], int)      # Heat Index -> integer or null
        row[12] = convert(row[12], float)    # Alt Pressure -> float or null
        row[13] = convert(row[13], float)    # Sea Pressure -> float or null
        row[14] = convert(row[14], float)    # 1HR Precip -> float or null
        row[15] = convert(row[15], float)    # 1HR Precip -> float or null
        row[16] = convert(row[16], float)    # 1HR Precip -> float or null
        # print(row)
    return data


def main():
    con = connect_to_db(DB_PATH)
    logger.info("Successfully connected to the observations database.")

    cur = con.cursor()
    stations = list(cur.execute("select * from station"))

    start_time = time.time()
    timed_out, incomplete, not_available = [], [], []
    statuses = {
        "TO": timed_out,
        "NA": not_available,
        "I": incomplete
    }

    for i, station in enumerate(stations):
        # Create a table for the station
        station = station[0]
        create_station_table(cur, station)

        data, status = get_raw_data(station)
        data_rows = format_rows(data)

        if status in statuses.keys():
            statuses[status].append(station)

        # Insert data into forecast table
        qmarks = ','.join(['?' for i in range(len(forecast_elements))])
        cur.executemany(
            f"""insert or replace into {station} values ({qmarks})""", data_rows
        )
        logger.debug(
            f"{station} table ({i+1-len(timed_out)}/{len(stations)}) updated."
        )

    con.commit()
    logger.info(
        "Initial observations update complete, "
        "now checking for timed out stations..."
    )
    logger.info(f"{len(timed_out)} stations timed out during first round.")

    current_round = 1
    while len(timed_out) > 0 and current_round <= 10:
        current_round += 1
        for i, station in enumerate(timed_out):
            # Create a table for the station
            create_station_table(cur, station)

            data, status = get_raw_data(station)
            data_rows = format_rows(data)

            if status in statuses.keys():
                statuses[status].append(station)

            # Insert data into forecast table
            qmarks = ','.join(['?' for i in range(len(forecast_elements))])
            cur.executemany(
                f"""insert or replace into {station} values ({qmarks})""", data_rows
            )
            logger.debug(
                f"{station} table ({len(timed_out) - (i+1)}/{len(stations)}) updated."
            )

            timed_out[i] = ''

        timed_out = list(filter(lambda x: x != '', timed_out))
        if len(timed_out) != 0:
            logger.info(
                f"Round {current_round} of re-requesting timed out URLs complete. "
                f"{len(timed_out)} stations still need updated."
            )

    if len(timed_out) != 0:  # pragma: no cover
        logger.warning(
            f"{len(timed_out)} stations could not be updated: "
            f"{', '.join(timed_out)}."
        )
    if len(incomplete) != 0:
        logger.warning(
            f"{len(incomplete)} stations had incomplete data: "
            f"{', '.join(incomplete)}."
        )

    if len(not_available) != 0:
        logger.warning(
            f"{len(not_available)} stations were not available: "
            f"{','.join(not_available)}."
        )

    con.commit()
    con.close()
    logger.info(
        f"Observations update complete after {current_round} rounds.\n"
        f"Completed in {time.time()-start_time} seconds."
    )
