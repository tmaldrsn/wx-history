import os
import pytest
from website import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    return client


@pytest.fixture
def valid_station():
    return "KTOL"


@pytest.fixture
def invalid_station():
    return "K000"


@pytest.mark.parametrize("page,title", [
    ('/', b"<title>NOAA Hourly Weather Observation Database</title>"),
    ('/stations/', b"<title>Stations List</title>"),
    ('/search/', b"<title>Search Database</title>")
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
