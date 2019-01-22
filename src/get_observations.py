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
from connect import (
    is_db_path,
    connect_to_db,
    get_observations_request,
    get_adjusted_date,
    get_datetime_string,
    get_datetime,
)
from bs4 import BeautifulSoup

fileConfig('logging_config.ini')
logger = logging.getLogger()

DB_PATH = "observations.db"
forecast_elements = [
    "Date",
    "Time",
    "Wind",
    "Visibility",
    "Weather",
    "Sky Condition",
    "Air Temperature",
    "Dew Point",
    "6HR Max",
    "6HR Min",
    "Humidty",
    "Wind Chill",
    "Heat Index",
    "Altimeter Pressure",
    "Sea Level Pressure",
    "1HR Precip",
    "3HR Precip",
    "6HR Precip"
]


def create_station_table(cur, station):
    try:
        obs_cols = ','.join('"{}"'.format(w) for w in forecast_elements)
        cur.execute(
            f"""create table if not exists {station} ({obs_cols}, constraint unq unique (date, time))""")
    except sqlite3.OperationalError:
        logger.info(f"Table not created for {station}")


def get_observation_list(station):
    try:
        req = get_observations_request(station)
        soup = BeautifulSoup(req, 'html.parser')
    except (OSError, URLError):
        logger.warning(f"Station {station} request timed out!!")
        return [], "TO"

    try:
        forecast_table = soup.find_all('table')[3]
        forecast_rows = forecast_table.find_all('tr')[3:-3]
    except IndexError:
        logger.warning(f"Station {station} data not available.")
        return [], "NA"
    else:
        if not forecast_rows:
            logger.warning(f"Station {station} data not available.")
            return [], "NA"

    most_recent_date = int(forecast_rows[0].find_all('td')[0].string)
    data_rows = []
    for _, row in enumerate(forecast_rows):
        obs_date = int(row.find_all('td')[0].string)
        obs_ordinal = [get_adjusted_date(most_recent_date, obs_date)]
        obs_list = [val.string for val in row.find_all('td')[1:]]
        data_rows.append(obs_ordinal + obs_list)

    if len(data_rows) < 30:
        return data_rows, "I"

    return data_rows, "G"


def main():
    con = connect_to_db(DB_PATH)
    logger.info("Successfully connected to the observations database.")

    cur = con.cursor()
    stations = list(cur.execute("select * from station"))

    start_time = time.time()
    timed_out, incomplete, not_available = [], [], []
    for i, station in enumerate(stations):
        # Create a table for the station
        station = station[0]
        create_station_table(cur, station)

        data_rows, status = get_observation_list(station)

        if status == "TO":
            timed_out.append(station)
            continue
        elif status == "NA":
            not_available.append(station)
            continue
        elif status == "I":
            incomplete.append(station)

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
        for i, station in enumerate(stations):
            # Create a table for the station
            create_station_table(cur, station)

            data_rows, status = get_observation_list(station)

            if status == "TO":
                timed_out.append(station)
                continue
            elif status == "NA":
                not_available.append(station)
                continue
            elif status == "I":
                incomplete.append(station)

            # Insert data into forecast table
            qmarks = ','.join(['?' for i in range(len(forecast_elements))])
            cur.executemany(
                f"""insert or replace into {station} values ({qmarks})""", data_rows
            )
            logger.debug(
                f"{station} table ({i+1-len(timed_out)}/{len(stations)}) updated."
            )

            timed_out[i] = ''

        timed_out = list(filter(lambda x: x != '', timed_out))
        if len(timed_out) != 0:
            logger.info(
                f"Round {current_round} of re-requesting timed out URLs complete. "
                f"{len(timed_out)} stations still need updated."
            )

    if len(timed_out) != 0:
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


if __name__ == '__main__':
    main()
