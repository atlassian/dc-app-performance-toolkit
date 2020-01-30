import pytest
import requests

# returns a logged in session for use in a test method
@pytest.fixture(scope="class")
def session():
    # authenticate to get a session id
    s = requests.session()
    auth_response = s.post('http://localhost:8080/rest/auth/1/session',
        json={ "username": "admin", "password": "admin" })
    return s
