import pytest
import datetime
import os
from src import connect


@pytest.fixture
def valid_date_string():
    return '01/01/2019'


@pytest.fixture
def valid_date_datetime():
    return datetime.datetime(2019, 1, 1, 0, 0)


def test_get_datetime(valid_date_string):
    assert connect.get_datetime(
        valid_date_string) == datetime.datetime(2019, 1, 1, 0, 0)


def test_db_path_verifies_db_file_is_true():
    assert connect.is_db_path('observations.db')


def test_db_path_verifies_db_file_is_false():
    assert not connect.is_db_path('observations.csv')


def test_adjusted_date_with_same_day_and_obs_day():
    today = datetime.datetime.today()
    today_string = "{0:02}/{1:02}/{2:04}".format(
        today.month, today.day, today.year
    )
    assert connect.get_adjusted_date(today.day, today.day) == today_string


def test_adjusted_date_over_month_transition():
    today = datetime.datetime(2000, 7, 1, 0, 0)
    adj_today = today - datetime.timedelta(minutes=15)
    today_string = "06/30/2000"
    assert connect.get_adjusted_date(
        today.day, adj_today.day, ref_date=today) == today_string


def test_adjusted_date_over_year_transition():
    today = datetime.datetime(2000, 1, 1, 0, 0)
    adj_today = today - datetime.timedelta(minutes=15)
    today_string = "12/31/1999"
    assert connect.get_adjusted_date(
        today.day, adj_today.day, ref_date=today) == today_string
