import pytest
import datetime
import os
import pandas as pd
from src import view_observations


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame(
        data=[
            ['12/30/2018', '12:52'],
            ['12/30/2018', '13:52'],
            ['12/30/2018', '14:52'],
            ['12/30/2018', '15:52']
        ],
        columns=["Date", "Time"]
    )


def test_get_datetimes_list_returns_datetimes_list(sample_dataframe):
    assert view_observations.get_datetimes_list(sample_dataframe) == [
        datetime.datetime(2018, 12, 30, 12, 52),
        datetime.datetime(2018, 12, 30, 13, 52),
        datetime.datetime(2018, 12, 30, 14, 52),
        datetime.datetime(2018, 12, 30, 15, 52)
    ]
