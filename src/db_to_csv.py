import sqlite3
import csv

from connect import is_db_path, get_db_cursor

DB = 'observations.db'


def convert_db_to_csv(db_path):
    if is_db_path(db_path):
        cur = get_db_cursor(db_path)
    else:
        raise Exception(f"{db_path} is not a valid database file.")

    station_query = "select * from station"
    station_list = list(cur.execute(station_query))

    with open('observations.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)

        for station in station_list:
            writer.writerow(station)

        for station in station_list:
            obs_query = f"select * from {station[0]} order by substr(date, 7, 4), substr(date, 1, 2), substr(date, 4, 2), time"
            observations = list(cur.execute(obs_query))

            for obs in observations:
                writer.writerow(tuple([station[0]] + list(obs)))


if __name__ == '__main__':
    convert_db_to_csv(DB)
