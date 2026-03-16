import pytest
import requests

from functionality.conftest import api, create_default, new_uuid, wait_for, create, Photo

invalid_customer_id = "MillieWasHere"
valid_customer_id = new_uuid()

def test_list_invalid_customer():
    """
    Checks for a 400 response from the statistics
    """
    response = requests.get(api('/analysis/' + invalid_customer_id + '/statistics'), headers={'Accept': 'application/json'})
    assert response.status_code == 400

def test_list_unknown_customer():
    """
    Checks for a 404 response from the statistics
    """
    response = requests.get(api('/analysis/' + new_uuid() + '/statistics'), headers={'Accept': 'application/json'})
    assert response.status_code == 404
