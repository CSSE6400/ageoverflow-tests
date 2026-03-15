import time
import uuid

import pytest
import requests

from functionality.conftest import api, create_untrusted_request, create_default_analysis_request, wait_for, new_uuid

invalid_customer_id = "MillieWasHere"
valid_customer_id = new_uuid()

def test_list_invalid_limit():
    """
    Checks for a 400 response from the analysis requests endpoint for invalid limit values
    """
    response = requests.get(api('/analysis/' + valid_customer_id + '/requests?limit=0'), headers={'Accept': 'application/json'})
    assert response.status_code == 400

    response = requests.get(api('/analysis/' + valid_customer_id + '/requests?limit=2000'), headers={'Accept': 'application/json'})
    assert response.status_code == 400

def test_list_invalid_offset():
    """
    Checks for a 400 response from the analysis requests endpoint for a negative offset
    """
    response = requests.get(api('/analysis/' + valid_customer_id + '/requests?offset=-1'), headers={'Accept': 'application/json'})
    assert response.status_code == 400

def test_list_invalid_date():
    """
    Checks for a 400 response from the analysis requests endpoint for a start and end time that are not valid
    """
    response = requests.get(api('/analysis/' + valid_customer_id + '/requests?start=not_a_time'), headers={'Accept': 'application/json'})
    assert response.status_code == 400

    response = requests.get(api('/analysis/' + valid_customer_id + '/requests?end=not_a_time'), headers={'Accept': 'application/json'})
    assert response.status_code == 400

def test_list_invalid_from():
    """
    Checks for a 400 response from the analysis requests endpoint for an invalid user_id filter
    """
    response = requests.get(api('/analysis/' + valid_customer_id + '/requests?user_id=billy'), headers={'Accept': 'application/json'})
    assert response.status_code == 400

def test_list_invalid_status():
    """
    Checks for a 400 response from the analysis requests endpoint for an invalid status filter
    """
    response = requests.get(api('/analysis/' + valid_customer_id + '/requests?status=sleepy'), headers={'Accept': 'application/json'})
    assert response.status_code == 400

def test_list_invalid_generation_only():
    """
    Checks for a 400 response from the analysis requests endpoint where the generation is an invalid value
    """
    response = requests.get(api('/analysis/' + valid_customer_id + '/requests?generation=zillennial'), headers={'Accept': 'application/json'})
    assert response.status_code == 400

def test_must_contain_photos():
    """
    Checks for a 400 response that the analysis requests endpoint correctly rejects inputs with no photo information
    """
    customer = new_uuid()
    user = new_uuid()
    response = create_untrusted_request(customer, user, photos=[])
    assert response.status_code == 400

@pytest.mark.timeout(300)
def test_list_default_length():
    """
    Checks for 100 analysis requests by default for the list endpoint
    """
    customer = new_uuid()
    items = [create_default_analysis_request(customer) for _ in range(102)]

    [wait_for(customer, item["id"]) for item in items]

    response = requests.get(api('/analysis/' + customer + '/requests'), headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 100

@pytest.mark.timeout(300)
def test_list_custom_length():
    """
    Checks custom lengths for the analysis requests endpoint, 5, 100 (with offset 5)
    """
    customer = new_uuid()
    items = [create_default_analysis_request(customer) for _ in range(20)]

    [wait_for(customer, item["id"]) for item in items]

    response = requests.get(api('/analysis/' + customer + '/requests?limit=5'), headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 5

    # Get the last id to check the offset
    second = response.json()[1]['id']

    response = requests.get(api('/analysis/' + customer + '/requests?limit=1&offset=1'), headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['id'] == second

