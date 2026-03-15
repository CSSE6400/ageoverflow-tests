import time
import uuid

import pytest
import requests

from rfc3339_validator import validate_rfc3339
from functionality.conftest import api, create_untrusted_request, create_default, wait_for, new_uuid, \
    Photo, get

invalid_customer_id = "MillieWasHere"
valid_customer_id = new_uuid()

def test_list_invalid_customer():
    """
    Checks for a 400 response from the analysis requests endpoint for invalid limit values
    """
    response = requests.get(api('/analysis/' + invalid_customer_id + '/requests?limit=0'), headers={'Accept': 'application/json'})
    assert response.status_code == 400

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
    user = new_uuid()
    response = create_untrusted_request(valid_customer_id, user, photos=[])
    assert response.status_code == 400

def test_must_contain_userid():
    """
    Checks for a 400 response that the analysis requests endpoint correctly rejects inputs with no user id information
    """
    response = requests.post(api('/analysis/' + valid_customer_id + '/requests'),
                             headers={ 'Accept': 'application/json' },
                             json={ 'urgent': False, 'photos': [Photo().as_payload()]})
    assert response.status_code == 400

def test_basic():
    """
    Checks for a 201 response and the minimal structure of the analysis requests endpoint
    """
    item = create_default(valid_customer_id)
    for field in ('id', 'user_id', 'created_at', 'updated_at', 'status'):
        assert field in item, f"Missing field: {field}"

    wait_for(valid_customer_id, item['id'])

    assert 'result' in item
    for field in ('checksum', 'primary_generation', 'age'):
        assert field in item['result'], f"Missing field: result.{field}"

    assert 'generations' in item['result']
    for field in ('silent', 'baby_boomers', 'x', 'y', 'z', 'alpha'):
        assert field in item['result']['generations'], f"Missing field: result.generations.{field}"

def test_basic_read():
    """
        Checks for a 201 response and the minimal structure of the analysis requests endpoint
    """
    item = create_default(valid_customer_id)
    wait_for(valid_customer_id, item['id'])
    item = get(valid_customer_id, item['id'])

    for field in ('id', 'user_id', 'created_at', 'updated_at', 'status'):
        assert field in item, f"Missing field: {field}"

    assert 'result' in item
    for field in ('checksum', 'primary_generation', 'age'):
        assert field in item['result'], f"Missing field: result.{field}"

    assert 'generations' in item['result']
    for field in ('silent', 'baby_boomers', 'x', 'y', 'z', 'alpha'):
        assert field in item['result']['generations'], f"Missing field: result.generations.{field}"

def test_request_user_id():
    """
    Checks that a successful request actually returns the user id we gave it
    """
    user = new_uuid()
    item = create_default(valid_customer_id, user)
    assert item['user_id'] == user

def test_request_timestamps_are_rfc3339():
    """
    Checks that a successful request has timestamps that are RFC 3339 format
    """
    item = create_default(valid_customer_id)
    for field in ('created_at', 'updated_at'):
        ts = item[field]
        assert validate_rfc3339(item[field]) is True, f"{field} is not RFC3339: {ts!r}"

def test_request_urgent():
    """
    Checks for a 201 response when urgent
    """
    item = create_default(valid_customer_id, urgent=True)
    wait_for(valid_customer_id, item['id'])
    get(valid_customer_id, item['id'])


@pytest.mark.timeout(300)
def test_list_default_length():
    """
    Checks for 100 analysis requests by default for the list endpoint
    """
    customer = new_uuid()
    items = [create_default(customer) for _ in range(102)]

    [wait_for(customer, item['id']) for item in items]

    response = requests.get(api('/analysis/' + customer + '/requests'), headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 100

@pytest.mark.timeout(300)
def test_list_custom_length():
    """
    Checks custom lengths for the analysis requests endpoint, 5, 100 (with offset 5)
    """
    items = [create_default(valid_customer_id) for _ in range(20)]

    [wait_for(valid_customer_id, item['id']) for item in items]

    response = requests.get(api('/analysis/' + valid_customer_id + '/requests?limit=5'), headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 5

    # Get the last id to check the offset
    second = response.json()[1]['id']

    response = requests.get(api('/analysis/' + valid_customer_id + '/requests?limit=1&offset=1'), headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['id'] == second

