import requests

from functionality.conftest import api


def test_health():
    """
    Checks for a 200 response from the health endpoint
    """
    response = requests.get(api('/health'), headers={'Accept': 'application/json'})
    assert response.status_code == 200
