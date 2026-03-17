import time
from urllib.parse import quote

import pendulum
import pytest
import requests

from rfc3339_validator import validate_rfc3339
from functionality.conftest import api, create_untrusted_request, create_default, wait_for, new_uuid, \
    Photo, get, Photos, create

invalid_customer_id = "MillieWasHere"
valid_customer_id = new_uuid()

def check_request_item(item: dict):
    for field in ('id', 'user_id', 'created_at', 'updated_at', 'status'):
        assert field in item, f"Missing field: {field}"

    assert item['status'] in ('success', 'pending', 'failed')

    if item['status'] == 'success':
        assert 'result' in item
        for field in ('checksum', 'primary_generation', 'age'):
            assert field in item['result'], f"Missing field: result.{field}"

        assert 'generations' in item['result']
        for field in ('silent', 'baby_boomers', 'x', 'y', 'z', 'alpha'):
            assert field in item['result']['generations'], f"Missing field: result.generations.{field}"


def test_list_invalid_customer():
    """
    Checks for a 400 response from the analysis requests endpoint for an invalid customer id
    """
    response = requests.get(api('/analysis/' + invalid_customer_id + '/requests'), headers={'Accept': 'application/json'})
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

def test_list_invalid_user_id():
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

    item = wait_for(valid_customer_id, item['id'])
    assert item['status'] == 'success'

    assert 'result' in item
    for field in ('checksum', 'primary_generation', 'age'):
        assert field in item['result'], f"Missing field: result.{field}"

    assert 'generations' in item['result']
    for field in ('silent', 'baby_boomers', 'x', 'y', 'z', 'alpha'):
        assert field in item['result']['generations'], f"Missing field: result.generations.{field}"

def test_multiple():
    """
    Checks for a 201 response and the minimal structure of the analysis requests endpoint with multiple photos
    """
    photos = Photos([
        Photo(complexity=0, age=22, silent=0, boomer=0, x=0, y=0, z=100, alpha=0),
        Photo(complexity=0, age=28, silent=0, boomer=0, x=0, y=50, z=50, alpha=0)
    ])
    item = create(valid_customer_id, user=new_uuid(), photos=photos.as_payload())
    item = wait_for(valid_customer_id, item['id'])
    check_request_item(item)

    assert item['result']['checksum'] == photos.checksum()



def test_basic_read():
    """
        Checks for a 201 response and the minimal structure of the analysis requests endpoint
    """
    item = create_default(valid_customer_id)
    wait_for(valid_customer_id, item['id'])
    item = get(valid_customer_id, item['id'])

    assert item['status'] == 'success'
    check_request_item(item)

def test_request_user_id():
    """
    Checks that a successful request actually returns the user id we gave it
    """
    user = new_uuid()
    item = create_default(valid_customer_id, user)
    assert item['user_id'] == user

def test_request_matches():
    """
    Checks that a successful request matches the Post response and Get response
    """
    item_post = create_default(valid_customer_id)
    item_get = get(valid_customer_id, item_post['id'])

    assert item_post['user_id'] == item_get['user_id']
    assert item_post['id'] == item_get['id']

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

def test_request_not_found():
    """
    Checks for a 404 response when a request is not found
    """
    create_default(valid_customer_id) # creates the customer
    response = requests.get(api(f"/analysis/{valid_customer_id}/requests/{new_uuid()}"), headers={'Accept': 'application/json'})
    assert response.status_code == 404

@pytest.mark.timeout(300)
def test_request_wrong_customer():
    """
    Checks for a 404 response when a request is not found but does exist but under a different customer
    """
    first_customer = new_uuid()
    first = create_default(first_customer) # creates the customer if needed

    second_customer = new_uuid()
    second = create_default(second_customer) # creates the customer if needed

    response = requests.get(api(f"/analysis/{first_customer}/requests/{second['id']}"), headers={'Accept': 'application/json'})
    assert response.status_code == 404

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
    Checks custom lengths for the analysis requests endpoint
    """
    customer = new_uuid()
    items = [create_default(customer) for _ in range(20)]

    [wait_for(customer, item['id']) for item in items]

    response = requests.get(api('/analysis/' + customer + '/requests?limit=5'), headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 5

    # Get the last id to check the offset
    second = response.json()[1]['id']

    response = requests.get(api('/analysis/' + customer + '/requests?limit=1&offset=1'), headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['id'] == second

    response = requests.get(api('/analysis/' + customer + '/requests?offset=20'))
    assert response.status_code == 200
    assert len(response.json()) == 0

@pytest.mark.timeout(300)
def test_list_filter_user():
    """
    Filters the list request by userid
    """
    customer = new_uuid()
    items = [create_default(customer) for _ in range(2)]

    response = requests.get(api('/analysis/' + customer + '/requests'), headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 2

    # Filters by a given userid
    response = requests.get(api('/analysis/' + customer + f"/requests?user_id={items[0]['user_id']}"), headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['id'] == items[0]['id']

    # Filters by an unknown userid
    response = requests.get(api('/analysis/' + customer + f"/requests?user_id={new_uuid()}"), headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 0

@pytest.mark.timeout(300)
def test_list_filter_status():
    """
    Filters the list request by status. Note this test is best effort due to the nature of it.
    """
    customer = new_uuid()
    item = create_default(customer)
    wait_for(customer, item['id'])

    response = requests.get(api('/analysis/' + customer + '/requests?status=success'), headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.timeout(30)
def test_list_requests_filter_date():
    """
    Filters the list request by date
    """
    customer = new_uuid()
    create_default(customer)

    # Any start date in the far future should return empty
    response = requests.get(api('/analysis/' + customer + '/requests?start=2099-01-01T00:00:00Z'),
                            headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 0

    # Any end date in the far past should return empty
    response = requests.get(api('/analysis/' + customer + '/requests?end=2000-01-01T00:00:00Z'),
                            headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 0

@pytest.mark.timeout(30)
def test_list_requests_filter_date_dynamic():
    """
    Filters the list request by date dynamically
    """
    customer = new_uuid()
    start = pendulum.now().replace(microsecond=0)
    item = create_default(customer)
    time.sleep(2)
    end = pendulum.now().replace(microsecond=0)

    # Debugging
    # print('start: ' + start.to_rfc3339_string())
    # print('request_created_at: ' + item['created_at'])
    # print('end: ' + end.to_rfc3339_string())

    time.sleep(5)
    create_default(customer)


    # Should only find the analysis request sent between start and end
    response = requests.get(api('/analysis/' + customer + f"/requests?start={quote(start.to_rfc3339_string())}&end={quote(end.to_rfc3339_string())}"),
                            headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 1

