import os
import pytest
from website import server


@pytest.fixture
def client():
    server.config['TESTING'] = True
    client = server.test_client()
    return client


@pytest.fixture
def valid_station():
    return "KTOL"


@pytest.fixture
def invalid_station():
    return "K000"


@pytest.mark.parametrize("page,title", [
    ('/', b"<title>Welcome | NOAA Hourly Observations</title>"),
    ('/stations/', b"<title>Stations List | NOAA Hourly Observations</title>"),
    ('/search/', b"<title>Search Database | NOAA Hourly Observations</title>")
])
def test_main_page_titles(client, page, title):
    page = client.get(page)
    assert title in page.get_data()


def test_negative_page_numbers_return_404(client):
    page = client.get('/stations/KTOL/-1')
    assert page.status_code == 404


def test_invalid_station_return_404(client, invalid_station):
    page = client.get('/ stations/' + invalid_station)
    assert page.status_code == 404
