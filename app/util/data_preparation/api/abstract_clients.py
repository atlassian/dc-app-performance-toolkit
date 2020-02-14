import json
from abc import ABC

import requests
from requests import Response


class Client(ABC):
    def __init__(self, host, user, password):
        self._host = host
        self._user = user
        self._password = password

    @property
    def host(self):
        return self._host

    @property
    def user(self):
        return self._user

    @property
    def password(self):
        return self._password


class RestClient(Client):
    JSON_HEADERS = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    @staticmethod
    def to_json(obj: dict) -> str:
        return json.dumps(obj)

    def __init__(self, host, user, password, session=None, timeout=30):
        super().__init__(host, user, password)

        self._requests_timeout = timeout
        self._session = session or requests.Session()

    @property
    def requests_timeout(self):
        return self._requests_timeout

    @property
    def session(self):
        return self._session

    @property
    def base_auth(self):
        return self.user, self.password

    def get(self, url: str, error_msg: str):
        response = self.session.get(url, auth=self.base_auth, verify=False, timeout=self.requests_timeout)
        self.__verify_response(response, error_msg)
        return response

    def post(self, url: str, error_msg: str, body: dict = None, params=None):
        body_data = self.to_json(body) if body else None
        response = self.session.post(url, body_data, params=params, auth=self.base_auth, headers=self.JSON_HEADERS)

        self.__verify_response(response, error_msg)
        return response

    def put(self, url: str, error_msg: str, body: dict = None, params=None):
        body_data = self.to_json(body) if body else None
        response = self.session.put(url, body_data, params=params, auth=self.base_auth, headers=self.JSON_HEADERS)

        self.__verify_response(response, error_msg)
        return response

    def __verify_response(self, response: Response, error_msg: str):
        if response.ok:
            return

        status_code = response.status_code
        if status_code == 403:
            denied_reason: str = response.headers.get('X-Authentication-Denied-Reason')
            if denied_reason and denied_reason.startswith('CAPTCHA_CHALLENGE'):
                raise Exception(f"User name [{self.user}] is in Captcha Mode. " +
                                "Please login via Web UI first and re-run tests.")

        raise Exception(f"{error_msg}. Response code:[{response.status_code}], response text:[{response.text}]")
