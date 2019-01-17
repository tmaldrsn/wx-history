import os
import pytest
from website import app


@pytest.fixture()
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    yield client


def test_negative_page_numbers_return_404(client):
    page = client.get('/stations/KTOL/-1')
    assert page.status_code == 404
