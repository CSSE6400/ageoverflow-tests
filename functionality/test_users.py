import pytest
import requests

from functionality.conftest import api, create_default, new_uuid, wait_for, create, Photo

invalid_customer_id = "MillieWasHere"
valid_customer_id = new_uuid()

def check_user(item: dict):
    assert 'id' in item
    assert 'results' in item
    for result in item['results']:
        assert 'id' in result
        assert 'status' in result
        assert 'checksum' in result
        assert 'primary_generation' in result
        assert 'age' in result

def test_list_invalid_customer():
    """
    Checks for a 400 response from the analysis users endpoint for an invalid customer id
    """
    response = requests.get(api('/analysis/' + invalid_customer_id + '/users'), headers={'Accept': 'application/json'})
    assert response.status_code == 400

def test_list_invalid_limit():
    """
    Checks for a 400 response from the analysis users endpoint for invalid limit values
    """
    response = requests.get(api('/analysis/' + valid_customer_id + '/users?limit=0'), headers={'Accept': 'application/json'})
    assert response.status_code == 400

    response = requests.get(api('/analysis/' + valid_customer_id + '/users?limit=2000'), headers={'Accept': 'application/json'})
    assert response.status_code == 400

def test_list_invalid_offset():
    """
    Checks for a 400 response from the analysis users endpoint for a negative offset
    """
    response = requests.get(api('/analysis/' + valid_customer_id + '/users?offset=-1'), headers={'Accept': 'application/json'})
    assert response.status_code == 400

@pytest.mark.timeout(300)
def test_basic():
    """
    Checks for 200 response and the structure of the analysis results in the user endpoint
    """
    user = new_uuid()
    req = create_default(valid_customer_id, user=user)
    wait_for(valid_customer_id, req['id'])

    response = requests.get(api('/analysis/' + valid_customer_id + '/users/' + user), headers={'Accept': 'application/json'})
    assert response.status_code == 200

    item = response.json()
    assert 'id' in item
    assert 'results' in item
    assert len(item['results']) == 1
    result = item['results'][0]
    assert 'id' in result
    assert result['id'] == req['id']
    assert 'status' in result
    assert result['status'] == 'success'
    assert 'checksum' in result
    assert result['checksum'] == '0x1d'
    assert 'primary_generation' in result
    assert result['primary_generation'] == 'y'
    assert 'age' in result
    assert result['age'] == 29

def test_list():
    """
    Checks for a single valid entry in the users list endpoint
    """
    user = new_uuid()
    req = create_default(valid_customer_id, user=user)
    wait_for(valid_customer_id, req['id'])

    response = requests.get(api('/analysis/' + valid_customer_id + '/users'), headers={'Accept': 'application/json'})
    assert response.status_code == 200

    for item in response.json():
        check_user(item)

def test_list_multiple():
    """
    Checks for multiple valid entries in the users list endpoint
    """
    customer = new_uuid()
    user_1 = new_uuid()
    photo_1 = Photo(complexity=0, age=22, silent=0, boomer=0, x=0, y=0, z=100, alpha=0)
    req = create(customer, user=user_1, photos=[photo_1.as_payload()])
    wait_for(customer, req['id'])

    user_2 = new_uuid()
    photo_2 = Photo(complexity=0, age=28, silent=0, boomer=0, x=0, y=50, z=50, alpha=0)
    req = create(customer, user=user_2, photos=[photo_2.as_payload()])
    wait_for(customer, req['id'])

    response = requests.get(api('/analysis/' + customer + '/users'), headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 2

    ages = [photo_1.age, photo_2.age]

    for item in response.json():
        check_user(item)
        assert item['results'][0]['age'] in ages

@pytest.mark.timeout(300)
def test_list_default_length():
    """
    Checks for 100 analysis requests by default for the users list endpoint, each user should have a unique UUIDv4
    """
    customer = new_uuid()
    items = [create_default(customer, user=new_uuid()) for _ in range(102)]

    [wait_for(customer, item['id']) for item in items]

    response = requests.get(api('/analysis/' + customer + '/users'), headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 100

@pytest.mark.timeout(300)
def test_list_custom_length():
    """
    Checks custom lengths for the users list endpoint (5 and 1 with an offset of 1)
    """
    customer = new_uuid()
    items = [create_default(customer, user=new_uuid()) for _ in range(20)]

    [wait_for(customer, item['id']) for item in items]

    response = requests.get(api('/analysis/' + customer + '/users?limit=5'), headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 5

    # Get the last id to check the offset
    second = response.json()[1]['id']

    response = requests.get(api('/analysis/' + customer + '/users?limit=1&offset=1'), headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['id'] == second
