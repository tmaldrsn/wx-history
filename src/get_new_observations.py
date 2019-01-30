import os
import sys
import random
import time
import datetime
import urllib.request
from urllib.error import URLError
import logging
from logging.config import fileConfig
from bs4 import BeautifulSoup

fileConfig('logging_config.ini')
logger = logging.getLogger()

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


def get_adjusted_date(day, obs_day, ref_date=None):
    if ref_date is None:
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


def main(station="KTOL"):
    try:
        req = urllib.request.urlopen(
            f"https://w1.weather.gov/data/obhistory/{station}.html", timeout=60)
        soup = BeautifulSoup(req, 'html.parser')
    except (OSError, URLError):
        logger.warning(f"Station {station} request timed out!!")
        return [], "TO"

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

    data_rows = []
    today = datetime.datetime.today()
    for _, row in enumerate(forecast_rows):
        obs_date = int(row.find_all('td')[0].string)
        obs_ordinal = ['{0:2d}/{1:2d}/{2:4d}'.format(
            today.month, obs_date, today.year)]
        obs_list = [val.string for val in row.find_all('td')[1:]]
        data_rows.append(obs_ordinal + obs_list)

    if len(data_rows) < 30:
        return data_rows, "I"

    return data_rows, "G"


if __name__ == '__main__':
    main()
