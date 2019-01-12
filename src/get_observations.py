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
    get_db_cursor,
    get_observations_request,
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


def db_insert_row(cursor, station):
    # TODO: figure out the best way to turn all the crap below into
    #       an easier to read function to put here.
    #       ideas:
    #           * iterate through rows and insert into db
    #           * iterate by station and insert table data
    #           * THINK DAMMIT
    pass


def main():
    # Create a database
    try:
        if not is_db_path(DB_PATH):
            raise Exception("Observations database does not exist!")
        else:
            con = sqlite3.connect(DB_PATH)
    except:
        raise Exception(
            "Was not able to connect to the observations database."
        )

    logger.info("Successfully connected to the observations database.")

    cur = con.cursor()
    stations = list(cur.execute("select * from station"))

    start_time = time.time()
    timed_out = []
    station_na = []
    for i, station in enumerate(stations):
        # Create a table for the station
        try:
            obs_cols = ','.join('"{}"'.format(w) for w in forecast_elements)
            cur.execute(
                f"""create table if not exists {station[0]} ({obs_cols}, constraint unq unique (date, time))""")
        except sqlite3.OperationalError:
            logger.info(f"Table not created for {station[0]}")
            pass

        try:
            req = get_observations_request(station[0])
            soup = BeautifulSoup(req, 'html.parser')
        except (OSError, URLError):
            logger.warning(f"Station {station[0]} request timed out!!")
            timed_out.append(station[0])
            continue

        try:
            forecast_table = soup.find_all('table')[3]
            forecast_rows = forecast_table.find_all('tr')[3:-3]
        except IndexError:
            logger.warning(f"Station {station[0]} data not available.")
            station_na.append(station[0])
            continue
        else:
            if not forecast_rows:
                logger.warning(f"Station {station[0]} data not available.")
                station_na.append(station[0])
                continue
            elif len(forecast_rows) < 30:
                logger.warning(f"Station {station[0]} data incomplete.")

        now_datetime = datetime.datetime.today()
        most_recent_year = now_datetime.year
        most_recent_month = now_datetime.month
        most_recent_day = int(forecast_rows[0].find_all('td')[0].string)

        if now_datetime.day == 1 and most_recent_day != 1:
            most_recent_month -= 1
            if most_recent_month == 0:
                most_recent_year -= 1
                most_recent_month = 12
        most_recent_date = datetime.date(
            year=most_recent_year,
            month=most_recent_month,
            day=most_recent_day
        )

        data_rows = []
        for _, row in enumerate(forecast_rows):
            obs_date = int(row.find_all('td')[0].string)
            if obs_date != most_recent_date.day:
                most_recent_date -= datetime.timedelta(days=1)

            #obs_ordinal = [most_recent_date.toordinal()]
            obs_ordinal = [most_recent_date.strftime("%m/%d/%Y")]
            obs_list = [val.string for val in row.find_all('td')[1:]]
            data_rows.append(obs_ordinal + obs_list)

        # Insert data into forecast table
        qmarks = ','.join(['?' for i in range(len(forecast_elements))])
        cur.executemany(
            f"""insert or replace into {station[0]} values ({qmarks})""", data_rows
        )
        logger.debug(
            f"{station[0]} table ({i+1-len(timed_out)}/{len(stations)}) updated."
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
            station = timed_out[i]
            try:
                req = get_observations_request(station)
                soup = BeautifulSoup(req, 'html.parser')
            except (OSError, URLError):
                logger.warning(
                    f"Station {station} request timed out again... "
                    "this time in round {current_round}"
                )
                continue

            now_datetime = datetime.datetime.today()
            most_recent_year = now_datetime.year
            most_recent_month = now_datetime.month
            most_recent_day = int(forecast_rows[0].find_all('td')[0].string)

            if now_datetime.day == 1 and most_recent_day != 1:
                most_recent_month -= 1
                if most_recent_month == 0:
                    most_recent_year -= 1
                    most_recent_month = 12
            most_recent_date = datetime.date(
                year=most_recent_year,
                month=most_recent_month,
                day=most_recent_day
            )

            data_rows = []
            for _, row in enumerate(forecast_rows):
                obs_date = int(row.find_all('td')[0].string)
                if obs_date != most_recent_date.day:
                    most_recent_date -= datetime.timedelta(days=1)

                obs_ordinal = [most_recent_date.strftime("%m/%d/%Y")]
                obs_list = [val.string for val in row.find_all('td')[1:]]
                data_rows.append(obs_ordinal + obs_list)

            # Insert data into forecast table
            qmarks = ','.join(['?' for i in range(len(forecast_elements))])
            cur.executemany(
                f"""insert or replace into {station} values ({qmarks})""", data_rows)
            logger.debug(
                f"{station} table ({len(stations)-len(timed_out)+i+1}/{len(stations)-len(station_na)}) updated."
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

    con.commit()
    con.close()
    logger.info(
        f"Observations update complete after {current_round} rounds.\n"
        f"Completed in {time.time()-start_time} seconds."
    )


if __name__ == '__main__':
    main()
