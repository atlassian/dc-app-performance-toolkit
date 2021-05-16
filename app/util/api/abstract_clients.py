import json
from abc import ABC

import requests
from requests import Response

JSON_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}
LOGIN_POST_HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9'
}

JSM_EXPERIMENTAL_HEADERS = {
    "Content-Type": "application/json",
    "X-ExperimentalApi": "opt-in"
}


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

    @staticmethod
    def to_json(obj: dict) -> str:
        return json.dumps(obj)

    def __init__(self, host, user, password, verify=False, headers=None, session=None, timeout=30):
        super().__init__(host, user, password)

        self._requests_timeout = timeout
        self._session = session or requests.Session()
        self.headers = headers if headers else JSON_HEADERS
        self.verify = verify

    @property
    def requests_timeout(self):
        return self._requests_timeout

    @property
    def session(self):
        return self._session

    @property
    def base_auth(self):
        return self.user, self.password

    def get(self, url: str,
            error_msg: str,
            expected_status_codes: list = None,
            allow_redirect: bool = False,
            headers: dict = None,
            auth: tuple = None):
        response = self.session.get(url, verify=self.verify, timeout=self.requests_timeout,
                                    allow_redirects=allow_redirect, headers=headers if headers else self.headers,
                                    auth=auth if auth else self.base_auth)
        self.__verify_response(response, error_msg, expected_status_codes)
        return response

    def delete(self, url: str, error_msg: str, expected_status_codes: list = None, allow_redirect=False):
        response = self.session.delete(url, auth=self.base_auth, verify=self.verify, timeout=self.requests_timeout,
                                       allow_redirects=allow_redirect)
        self.__verify_response(response, error_msg, expected_status_codes)
        return response

    def post(self, url: str,
             error_msg: str,
             body: dict = None,
             params: dict = None,
             files: dict = None,
             allow_redirect: bool = False,
             headers: dict = None,
             auth: tuple = None):
        body_data = self.to_json(body) if body else None
        response = self.session.post(url, body_data, params=params, files=files,
                                     auth=auth if auth else self.base_auth,
                                     headers=headers if headers else self.headers,
                                     allow_redirects=allow_redirect, verify=self.verify)

        self.__verify_response(response, error_msg)
        return response

    def put(self, url: str, error_msg: str, body: dict = None, params=None, allow_redirect=False):
        body_data = self.to_json(body) if body else None
        response = self.session.put(url, body_data, params=params, auth=self.base_auth, headers=self.headers,
                                    allow_redirects=allow_redirect, verify=self.verify)

        self.__verify_response(response, error_msg)
        return response

    def __verify_response(self, response: Response, error_msg: str, expected_status_codes: list = None):
        if response.is_redirect:
            raise Exception(f"Redirect detected.\n "
                            f"Please check config.yml file (application_hostname, application_port, "
                            f"application_protocol, application_postfix).")
        if response.ok or (expected_status_codes and response.status_code in expected_status_codes):
            return

        status_code = response.status_code
        if status_code == 403:
            denied_reason: str = response.headers.get('X-Authentication-Denied-Reason')
            if denied_reason and denied_reason.startswith('CAPTCHA_CHALLENGE'):
                raise Exception(f"User name [{self.user}] is in Captcha Mode. " +
                                "Please login via Web UI first and re-run tests.")
        elif status_code == 404:
            raise Exception(f"The URL or content are not found for {response.url}. "
                            f"Please check environment variables in "
                            f"config.yml file (application_hostname, application_port, application_protocol, "
                            f"application_postfix).")
        raise Exception(f"{error_msg}. Response code:[{response.status_code}], response text:[{response.text}]")
