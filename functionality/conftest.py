import base64
import json
import os
import time
import uuid

import lorem
import requests
from requests import Response

BASE_URL = os.getenv("TEST_HOST", "http://172.17.0.1:8080/api/v1").removesuffix("/")

def api(path: str) -> str:
    return f"{BASE_URL}{path}"

def new_uuid() -> str:
    return str(uuid.uuid4())

def wait_for(customer: str, request_id: str, timeout: int = 180, interval: int = 2) -> dict|None:
    """Poll GET /analysis/{customer_id}/requests/{request_id} until status != 'pending'.

    Returns the final response dict, or None if timeout is reached.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        response = requests.get(api(f"/analysis/{customer}/requests/{request_id}"))
        if response.status_code == 200:
            data = response.json()
            if data.get("status") != "pending":
                return data
        time.sleep(interval)
    return None

def create_untrusted_request(customer: str, user: str, photos: list[str], urgent: bool = False) -> Response:
    response = requests.post(api('/analysis/' + customer + '/requests'),
                             headers={'Accept': 'application/json'}, json={
            "user_id": user,
            "urgent": urgent,
            "photos": photos
        })
    return response

def create(customer: str, user: str, photos: list[str], urgent: bool = False) -> dict:
    response = create_untrusted_request(customer, user, photos, urgent)
    assert response.status_code == 201
    return response.json()

def create_default(customer: str, user: str | None = None, urgent: bool = False) -> dict:
    """
    Creates a small analysis request which completes instantly for unit testing purposes
    """
    if user is None:
        user = new_uuid()

    photo = Photo().as_payload()
    return create(customer, user, photos=[photo], urgent=urgent)

def get(customer: str, request_id: str) -> dict:
    """
    Get a request by customer and request id
    """
    response = requests.get(api(f"/analysis/{customer}/requests/{request_id}"))
    assert response.status_code == 200
    return response.json()

class Photo:

    def __init__(self, complexity: int = 0, age: int = 29, silent: int = 0, boomer: int = 0, x: int = 0, y: int = 60, z: int = 40, alpha: int = 0, filler: str|None = None):
        if filler is None:
            filler = lorem.sentence()

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
        return str(base64.b64encode(encoded.encode('utf-8')), 'utf-8')

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