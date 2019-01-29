from connect import is_db_path
import sqlite3
import csv
import logging
from logging.config import fileConfig
fileConfig('logging_config.ini')
logger = logging.getLogger()

DB = 'observations.db'


def convert_db_to_csv(db_path):
    if not is_db_path(db_path):
        raise Exception(f"{db_path} is not a valid database file.")

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    station_query = "select * from station"
    station_list = list(cur.execute(station_query))

    with open('observations.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)

        writer.writerow(['ID', 'State', 'Name', 'Latitude', 'Longitude'])
        for station in station_list:
            writer.writerow(station)
        logger.info("Station data written.")

        writer.writerow(['Station', 'Date', 'Time', 'Wind', 'Visibility', 'Weather', 'Sky Condition', 'Air Temperature', 'Dew Point', '6HR Max', '6HR Min',
                         'Humidity', 'Wind Chill', 'Heat Index', 'Altimeter Pressure', 'Sea Level Pressure', '1HR Precip', '3HR Precip', '6HR Precip'])
        for station in station_list:
            obs_query = f"select * from {station[0]} order by substr(date, 7, 4), substr(date, 1, 2), substr(date, 4, 2), time"
            observations = list(cur.execute(obs_query))

            for obs in observations:
                writer.writerow(tuple([station[0]] + list(obs)))
            logger.debug(f"{station[0]} data written to csv file.")
        logger.info("Observation data to csv complete.")


if __name__ == '__main__':
    convert_db_to_csv(DB)
