import time

import pendulum
import pytest
import requests
from retry import retry
from rfc3339_validator import validate_rfc3339

from functionality.conftest import api, create_default, new_uuid, wait_for, create, Photo

invalid_customer_id = "MillieWasHere"
valid_customer_id = new_uuid()

def get_stats(customer_id):
    response = requests.get(api(f"/analysis/{customer_id}/statistics"))
    assert response.status_code == 200
    return response.json()['contents']

def test_list_invalid_customer():
    """
    Checks for a 400 response from the statistics endpoint for an invalid customer id
    """
    response = requests.get(api('/analysis/' + invalid_customer_id + '/statistics'), headers={'Accept': 'application/json'})
    assert response.status_code == 400

def test_list_unknown_customer():
    """
    Checks for a 404 response from the statistics endpoint for a non-existent customer
    """
    response = requests.get(api('/analysis/' + new_uuid() + '/statistics'), headers={'Accept': 'application/json'})
    assert response.status_code == 404

@pytest.mark.timeout(480)
def test_single_entry():
    """
    Checks statistical values for a single entry
    """
    customer = new_uuid()
    item = create_default(customer, user=new_uuid())
    item = wait_for(customer, item['id'])

    @retry(AssertionError, tries=12, delay=30)
    def _check():
        stats = get_stats(customer)
        assert stats['total_requests'] == 1
        assert stats['total_users'] == 1
        assert stats['mean'] == 29
        assert stats['median'] == 29
        assert stats['buckets']['20'] == 1
        assert stats['buckets']['30'] == 0
        assert stats['buckets']['40'] == 0
        assert stats['buckets']['50'] == 0
        assert stats['buckets']['60'] == 0
        assert stats['buckets']['70'] == 0
        assert stats['buckets']['80'] == 0

    _check()

@pytest.mark.timeout(480)
def test_two_entries():
    """
    Checks statistical values for two entries
    """
    customer = new_uuid()
    user = new_uuid()

    req = create(customer, user=user, photos=[Photo(complexity=0, age=22, silent=0, boomer=0, x=0, y=0, z=100, alpha=0).as_payload()])
    wait_for(customer, req['id'])

    req = create(customer, user=user, photos=[Photo(complexity=0, age=28, silent=0, boomer=0, x=0, y=50, z=50, alpha=0).as_payload()])
    item = wait_for(customer, req['id'])

    @retry(AssertionError, tries=12, delay=30)
    def _check():
        stats = get_stats(customer)
        assert stats['total_requests'] == 2
        assert stats['total_users'] == 1
        assert abs(stats['mean'] - 25) < 0.001 or abs(stats['mean'] - 22.06) < 0.001
        assert abs(stats['median'] - 25) < 0.001 or abs(stats['median'] - 22.01) < 0.001
        assert stats['buckets']['20'] == 2
        assert stats['buckets']['30'] == 0
        assert stats['buckets']['40'] == 0
        assert stats['buckets']['50'] == 0
        assert stats['buckets']['60'] == 0
        assert stats['buckets']['70'] == 0
        assert stats['buckets']['80'] == 0

    _check()

@pytest.mark.timeout(360)
def test_multiple_entries():
    """
    Checks statistical values for multiple entries
    """
    customer = new_uuid()
    user = new_uuid()

    req = create(customer, user=user, photos=[Photo(complexity=0, age=22, silent=0, boomer=0, x=0, y=0, z=100, alpha=0).as_payload()])
    wait_for(customer, req['id'])

    req = create(customer, user=user, photos=[Photo(complexity=0, age=28, silent=0, boomer=0, x=0, y=50, z=50, alpha=0).as_payload()])
    wait_for(customer, req['id'])

    req = create(customer, user=new_uuid(), photos=[Photo(complexity=0, age=40, silent=0, boomer=0, x=70, y=30, z=0, alpha=0).as_payload()])
    wait_for(customer, req['id'])

    @retry(AssertionError, tries=12, delay=30)
    def _check():
        stats = get_stats(customer)
        assert stats['total_requests'] == 3
        assert stats['total_users'] == 2
        assert abs(stats['mean'] - 30) < 0.001 or abs(stats['mean'] - 22.24) < 0.01
        assert abs(stats['median'] - 28) < 0.001 or abs(stats['median'] - 22.02) < 0.001
        assert stats['buckets']['20'] == 2
        assert stats['buckets']['30'] == 0
        assert stats['buckets']['40'] == 1
        assert stats['buckets']['50'] == 0
        assert stats['buckets']['60'] == 0
        assert stats['buckets']['70'] == 0
        assert stats['buckets']['80'] == 0

    _check()

@pytest.mark.timeout(480)
def test_generated_at():
    """
    Checks that the generated at is incrementing
    """
    start = pendulum.now().replace(microsecond=0)
    customer = new_uuid()
    item = create_default(customer, user=new_uuid())
    item = wait_for(customer, item['id'])

    @retry(AssertionError, tries=12, delay=30)
    def _check():
        response = requests.get(api(f"/analysis/{customer}/statistics"))
        payload = response.json()
        assert response.status_code == 200
        assert payload['contents']['total_requests'] == 1
        assert validate_rfc3339(payload['generated_at']) is True
        assert pendulum.parse(payload['generated_at']) > start

    _check()