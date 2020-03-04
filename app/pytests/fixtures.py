import pytest
import requests
import os
import random
import time
import pathlib
import yaml
import json
from os import path
from requests import Session


def env_settings():
    basepath = path.dirname(__file__)
    filepath = path.abspath(path.join(basepath, "..", "jira.yml"))
    print(filepath)
    with open(filepath) as file:
        dict= yaml.load(file)
    envSetting = dict['settings']['env']
    return envSetting

def get_hostname_port():
    envSetting = env_settings()
    print(envSetting)
    hostname_port_var = 'http://' + envSetting['application_hostname'] + ':' + str(envSetting['application_port'])
    return hostname_port_var


BASE_URL = get_hostname_port()


@pytest.fixture
def base_url():
    return BASE_URL

@pytest.fixture
def nr_projects():
    envSettings = env_settings()
    return envSettings['max_nr_projects_to_use']

class LiveServerSession(Session):
    def __init__(self, prefix_url=None, *args, **kwargs):
        super(LiveServerSession, self).__init__(*args, **kwargs)
        self.prefix_url = prefix_url
    def request(self, method, url, *args, **kwargs):
        url = self.prefix_url + url
        return super(LiveServerSession, self).request(method, url, *args, **kwargs)


# get list of all users - except 'admin' if more than one user
print("hej")
print(BASE_URL);
users_reponse = requests.get(BASE_URL  + '/rest/api/latest/user/search?username=.', auth=('admin', 'admin'))
assert users_reponse.status_code == 200
users = list(map(lambda user : user['name'], users_reponse.json()))
if len(users) > 1 and 'admin' in users:
    users.remove('admin')
#print(users)




# returns a random username/password dict
# all users have password 'password', except user 'admin' that has password 'admin'
def getRandomUsernamePassword():
    username = random.choice(users)
    password = 'password'
    if username == 'admin':
        password = 'admin'
 #   print(username)
 #   print("RETURN USER: " + username)
    return {'username': username, 'password': password}

# returns a logged in session for use in a test method
@pytest.fixture(scope="class")
def session():
 #   time.sleep(20)
 #   print("create session")
    # authenticate to get a session id
    s =  LiveServerSession(BASE_URL)
    auth_response = s.post('/rest/auth/1/session',
                           json=getRandomUsernamePassword())

    # after test teardown
    yield s  # provide the fixture value
    print("teardown session")
    s.close()
    return s

# returns hostname_port
#@pytest.fixture(scope="class")
#def hostnameport():
#    return get_hostname_port()
