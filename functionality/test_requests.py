import time
import unittest
import uuid
import requests

from rfc3339_validator import validate_rfc3339
from .base import BaseCase


class TestRequests(BaseCase):

    invalid_customer_id = "MillieWasHere"
    valid_customer_id = uuid.uuid4().__str__()

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
        [self.create_default_analysis_request(customer) for _ in range(102)]

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
            self.create_default_analysis_request(customer)
        
        time.sleep(10) # wait for the scans to finish even though not needed.

        response = requests.get(self.host() + '/analysis/' + customer + '/requests?limit=5', headers={'Accept': 'application/json'})
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.json()), 5)

        # Get the last id to check the offset
        second = response.json()[1]['id']

        response = requests.get(self.host() + '/analysis/' + customer + '/requests?limit=1&offset=1', headers={'Accept': 'application/json'})
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['id'], second)

if __name__ == '__main__':
    unittest.main()
