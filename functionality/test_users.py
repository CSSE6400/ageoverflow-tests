import time
import unittest
import uuid
import requests

from .base import BaseCase

class TestUsers(BaseCase):

    invalid_customer_id = "MillieWasHere"
    valid_customer_id = uuid.uuid4().__str__()

    def test_list_invalid_limit(self):
        """
        Checks for a 400 response from the analysis requests endpoint for invalid limit values
        """
        response = requests.get(self.host() + '/analysis/' + self.valid_customer_id + '/users?limit=0', headers={'Accept': 'application/json'})
        self.assertEqual(400, response.status_code)

        response = requests.get(self.host() + '/analysis/' + self.valid_customer_id + '/users?limit=2000', headers={'Accept': 'application/json'})
        self.assertEqual(400, response.status_code)

    def test_list_invalid_offset(self):
        """
        Checks for a 400 response from the analysis requests endpoint for a negative offset
        """
        response = requests.get(self.host() + '/analysis/' + self.valid_customer_id + '/users?offset=-1', headers={'Accept': 'application/json'})
        self.assertEqual(400, response.status_code)

    def test_list_default_length(self):
        """
        Checks for 100 analysis requests by default for the list endpoint, each should get a unique UUIDv4 customer
        """
        customer = uuid.uuid4().__str__()
        [self.create_default_analysis_request(customer, user=uuid.uuid4().__str__()) for _ in range(102)]

        time.sleep(70) # wait for the scans to finish

        response = requests.get(self.host() + '/analysis/' + customer + '/users', headers={'Accept': 'application/json'})
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.json()), 100)

    def test_list_custom_length(self):
        """
        Checks custom lengths for the analysis requests endpoint, 5, 100 (with offset 5)
        """
        customer = uuid.uuid4().__str__()
        for _ in range(20):
            self.create_default_analysis_request(customer, user=uuid.uuid4().__str__())
        
        time.sleep(10) # wait for the scans to finish even though not needed.

        response = requests.get(self.host() + '/analysis/' + customer + '/users?limit=5', headers={'Accept': 'application/json'})
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.json()), 5)

        # Get the last id to check the offset
        second = response.json()[1]['id']

        response = requests.get(self.host() + '/analysis/' + customer + '/users?limit=1&offset=1', headers={'Accept': 'application/json'})
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['id'], second)

if __name__ == '__main__':
    unittest.main()
