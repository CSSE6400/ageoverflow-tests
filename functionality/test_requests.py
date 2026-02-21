import time
import unittest
from urllib.parse import quote
import uuid
import requests
import random
import lorem
import pendulum
import json
import base64

from rfc3339_validator import validate_rfc3339
from .base import BaseCase

class Photo:

    def __init__(self, complexity, age, silent, boomer, x, y, z, alpha, filler=lorem.sentence()):
        self.complexity = complexity
        self.age = age
        self.silent = silent
        self.boomer = boomer
        self.x = x
        self.y = y
        self.z = z
        self.alpha = alpha
        self.filler = filler

    def to_dict(self):
        return self.__dict__

    def as_payload(self):
        encoded = f"{self.complexity}|{self.age}|{self.silent}|{self.boomer}|{self.x}|{self.y}|{self.z}|{self.alpha}|{self.filler}"
        return base64.b64encode(json.dumps(encoded).encode('utf-8'))

    def checksum(self):
        return hex(self.age)

class Photos:

    def __init__(self, photos: list[Photo]):
        self.photos = photos

    def to_dict(self):
        return self.__dict__

    def checksum(self):
        total = 0
        for photo in self.photos:
            total += photo.age
        return hex(total)

class TestRequests(BaseCase):

    invalid_customer_id = "MillieWasHere"
    valid_customer_id = uuid.uuid4().__str__()

    def create_untrusted_request(self, customer, user, photos, urgent=False):
        response = requests.post(self.host() + '/analysis/' + customer + '/requests', headers={'Accept': 'application/json'}, json={
            "user_id": user,
            "urgent": urgent,
            "photos": photos
        })
        return response

    def create_request(self, customer, user, photos, urgent=False):
        response = self.create_untrusted_request(customer, user, photos, urgent)
        self.assertEqual(201, response.status_code, response.text)
        return response

    def create_default_analysis_request(self, customer):
        """
        Creates a small analysis request which completes instantly for unit testing purposes
        """
        return self.create_request(customer, user, photo=[Photo().as_payload])
        
    
    def wait_for_scan(self, customer, request_id, timeout=3):
        timeout = time.time() + (20 * timeout) + 30  # 30 seconds to account for the time it takes to test the output
        while time.time() <= timeout:
            response = requests.get(self.host() + '/analysis/' + customer + '/requests/' + request_id, headers={'Accept': 'application/json'})

            if time.time() > timeout:
                self.fail("Scan results were not available in time")

            self.assertEqual(200, response.status_code)

            if response.json().get('status') not in ['pending', 'scanned']:
                self.fail('Status was not correct: ' + response.json().get('status'))

            if response.json().get('status') == 'scanned':
                return response.json()

        self.fail('request not processed successfully within timelimit')

    def test_non_existent_customer(self):
        """
        Checks for a 400 response from the analysis endpoint for a customer that does not exist
        """
        response = requests.get(self.host() + '/analysis/' + self.invalid_customer_id + '/requests', headers={'Accept': 'application/json'})
        self.assertEqual(404, response.status_code)

    def test_list_invalid_limit(self):
        """
        Checks for a 400 response from the analysis requests endpoint for invalid limit values
        """
        response = requests.get(self.host() + '/analysis/' + self.valid_customer_id + '/requests?limit=0', headers={'Accept': 'application/json'})
        self.assertEqual(400, response.status_code)

        response = requests.get(self.host() + '/analysis/' + self.valid_customer_id + '/requests?limit=2000', headers={'Accept': 'application/json'})
        self.assertEqual(400, response.status_code)

    def test_list_invalid_offset(self):
        """
        Checks for a 400 response from the analysis requests endpoint for a negative offset
        """
        response = requests.get(self.host() + '/analysis/' + self.valid_customer_id + '/requests?offset=-1', headers={'Accept': 'application/json'})
        self.assertEqual(400, response.status_code)

    def test_list_invalid_date(self):
        """
        Checks for a 400 response from the analysis requests endpoint for a start and end time that are not valid
        """
        response = requests.get(self.host() + '/analysis/' + self.valid_customer_id + '/requests?start=not_a_time', headers={'Accept': 'application/json'})
        self.assertEqual(400, response.status_code)

        response = requests.get(self.host() + '/analysis/' + self.valid_customer_id + '/requests?end=not_a_time', headers={'Accept': 'application/json'})
        self.assertEqual(400, response.status_code)

    def test_list_invalid_from(self):
        """
        Checks for a 400 response from the analysis requests endpoint for an invalid user_id filter
        """
        response = requests.get(self.host() + '/analysis/' + self.valid_customer_id + '/requests?user_id=billy', headers={'Accept': 'application/json'})
        self.assertEqual(400, response.status_code)

    def test_list_invalid_status(self):
        """
        Checks for a 400 response from the analysis requests endpoint for an invalid status filter
        """
        response = requests.get(self.host() + '/analysis/' + self.valid_customer_id + '/requests?status=sleepy', headers={'Accept': 'application/json'})
        self.assertEqual(400, response.status_code)

    def test_list_invalid_generation_only(self):
        """
        Checks for a 400 response from the analysis requests endpoint where the generation is an invalid value
        """
        response = requests.get(self.host() + '/analysis/' + self.valid_customer_id + '/requests?generation=zillennial', headers={'Accept': 'application/json'})
        self.assertEqual(400, response.status_code)

    def test_must_contain_photos(self):
        """
        Checks for a 400 response that the analysis requests endpoint correctly rejects inputs with no photo information
        """
        customer = uuid.uuid4().__str__()
        user = uuid.uuid4().__str__()
        response = self.create_untrusted_request(customer, user, photos=[])
        self.assertEqual(400, response.status_code)

    def test_list_default_length(self):
        """
        Checks for 100 analysis requests by default for the list endpoint
        """
        customer = uuid.uuid4().__str__()
        [self.create_default_analysis_request(customer, False) for _ in range(102)]

        time.sleep(70) # wait for the scans to finish

        response = requests.get(self.host() + '/analysis/' + customer + '/requests', headers={'Accept': 'application/json'})
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.json()), 100)

    def test_list_custom_length(self):
        """
        Checks custom lengths for the analysis requests endpoint, 5, 100 (with offset 5)
        """
        customer = uuid.uuid4().__str__()
        for _ in range(20):
            self.create_default_email(customer, False)
        
        time.sleep(10) # wait for the scans to finish even though not needed.

        response = requests.get(self.host() + '/analysis/' + customer + '/requests?limit=5', headers={'Accept': 'application/json'})
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.json()), 5)

        response = requests.get(self.host() + '/analysis/' + customer + '/requests?limit=100&offset=5', headers={'Accept': 'application/json'})
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.json()), 15)

if __name__ == '__main__':
    unittest.main()
