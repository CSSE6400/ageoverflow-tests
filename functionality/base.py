import base64
import json
import time
import unittest
import os
import uuid

import lorem
import requests


class BaseCase(unittest.TestCase):
    def host(self):
        base = os.environ.get('TEST_HOST', 'http://172.17.0.1:8080/api/v1')
        if base[-1] == '/':
            return base[:-1]
        return base

    def assertDictSubset(self, expected_subset: dict, whole: dict, dict_sort=lambda d: d['name']):
        for key, value in expected_subset.items():
            if key not in whole:
                self.assertFalse(True, f'Key {key} not found in {whole}')
            if isinstance(value, dict):
                self.assertDictSubset(value, whole[key])

            if isinstance(value, list):
                if len(value) > 0 and isinstance(value[0], dict):
                    self.assertEqual(sorted(value, key=dict_sort), sorted(whole[key], key=dict_sort))
                else:
                    self.assertEqual(sorted(value), sorted(whole[key]))
            else:
                self.assertEqual(value, whole[key])

    def create_untrusted_request(self, customer, user, photos, urgent=False):
        response = requests.post(self.host() + '/analysis/' + customer + '/requests',
                                 headers={'Accept': 'application/json'}, json={
                "user_id": user,
                "urgent": urgent,
                "photos": photos
            })
        return response

    def create_request(self, customer, user, photos, urgent=False):
        response = self.create_untrusted_request(customer, user, photos, urgent)
        self.assertEqual(201, response.status_code, response.text)
        return response

    def create_default_analysis_request(self, customer, user=uuid.uuid4().__str__()):
        """
        Creates a small analysis request which completes instantly for unit testing purposes
        """
        photo = Photo().as_payload()
        return self.create_request(customer, user, photos=[photo])

    def wait_for_scan(self, customer, request_id, timeout=3):
        timeout = time.time() + (20 * timeout) + 30  # 30 seconds to account for the time it takes to test the output
        while time.time() <= timeout:
            response = requests.get(self.host() + '/analysis/' + customer + '/requests/' + request_id,
                                    headers={'Accept': 'application/json'})

            if time.time() > timeout:
                self.fail("Scan results were not available in time")

            self.assertEqual(200, response.status_code)

            if response.json().get('status') not in ['pending', 'scanned']:
                self.fail('Status was not correct: ' + response.json().get('status'))

            if response.json().get('status') == 'scanned':
                return response.json()

        self.fail('request not processed successfully within timelimit')


class Photo:

    def __init__(self, complexity = 0, age = 29, silent = 0, boomer = 0, x = 0, y = 60, z = 40, alpha = 0, filler=lorem.sentence()):
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
        return str(base64.b64encode(json.dumps(encoded).encode('utf-8')), "utf-8")

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