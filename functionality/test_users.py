import pytest
import requests

from functionality.conftest import api, create_default, new_uuid, wait_for

invalid_customer_id = "MillieWasHere"
valid_customer_id = new_uuid()

def test_list_invalid_limit():
    """
    Checks for a 400 response from the analysis requests endpoint for invalid limit values
    """
    response = requests.get(api('/analysis/' + valid_customer_id + '/users?limit=0'), headers={'Accept': 'application/json'})
    assert response.status_code == 400

    response = requests.get(api('/analysis/' + valid_customer_id + '/users?limit=2000'), headers={'Accept': 'application/json'})
    assert response.status_code == 400

def test_list_invalid_offset():
    """
    Checks for a 400 response from the analysis requests endpoint for a negative offset
    """
    response = requests.get(api('/analysis/' + valid_customer_id + '/users?offset=-1'), headers={'Accept': 'application/json'})
    assert response.status_code == 400

@pytest.mark.timeout(300)
def test_list_default_length():
    """
    Checks for 100 analysis requests by default for the list endpoint, each should get a unique UUIDv4 customer
    """
    customer = new_uuid()
    items = [create_default(customer, user=new_uuid()) for _ in range(102)]

    [wait_for(customer, item["id"]) for item in items]

    response = requests.get(api('/analysis/' + customer + '/users'), headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 100

@pytest.mark.timeout(300)
def test_list_custom_length():
    """
    Checks custom lengths for the analysis requests endpoint, 5, 100 (with offset 5)
    """
    customer = new_uuid()
    items = [create_default(customer, user=new_uuid()) for _ in range(20)]

    [wait_for(customer, item["id"]) for item in items]

    response = requests.get(api('/analysis/' + customer + '/users?limit=5'), headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 5

    # Get the last id to check the offset
    second = response.json()[1]['id']

    response = requests.get(api('/analysis/' + customer + '/users?limit=1&offset=1'), headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['id'] == second
