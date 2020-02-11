import pytest
import requests
import os

# returns a logged in session for use in a test method
@pytest.fixture(scope="class")
def session():
    print("create session")
    # authenticate to get a session id
    s = requests.session()
    HOSTNAME = os.environ.get('application_hostname')
    auth_response = s.post('http://' + HOSTNAME + ':8080/rest/auth/1/session',
                           json={ "username": "admin", "password": "admin" })

    # after test teardown
    yield s  # provide the fixture value
    print("teardown session")
    s.close()
    return s
