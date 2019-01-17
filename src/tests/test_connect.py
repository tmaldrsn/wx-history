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
