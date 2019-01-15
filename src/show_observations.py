import os
import sys
import sqlite3
import tabulate
import logging
from logging.config import fileConfig

fileConfig('logging_config.ini')
logger = logging.getLogger()
DB = "observations.db"
STATION = "KTOL"


def main(station=STATION):
    if not os.path.isfile(DB):
        raise Exception("Observations database does not exist!")

    con = sqlite3.connect(DB)
    cur = con.cursor()

    logger.info(f"Successfully logged into observations database")

    header_query = f"pragma table_info({station})"
    data_query = f"select * from {station} order by substr(date, 7, 4), substr(date, 1, 2), substr(date, 4, 2), time"

    print(f"DATA FROM STATION {station}")
    print(tabulate.tabulate(list(cur.execute(data_query)), headers=[
          i[1] for i in list(cur.execute(header_query))], tablefmt="plain"))


if __name__ == '__main__':
    if len(sys.argv) == 2:
        STATION = sys.argv[1]
    else:
        STATION = "KTOL"
    main(STATION)
