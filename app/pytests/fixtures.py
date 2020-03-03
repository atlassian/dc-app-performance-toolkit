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

BASE_URL="http://localhost:8080"

@pytest.fixture
def base_url():
    return BASE_URL

class LiveServerSession(Session):
    def __init__(self, prefix_url=None, *args, **kwargs):
        super(LiveServerSession, self).__init__(*args, **kwargs)
        self.prefix_url = prefix_url
    def request(self, method, url, *args, **kwargs):
        url = self.prefix_url + url
        return super(LiveServerSession, self).request(method, url, *args, **kwargs)

def get_hostname_port():
    basepath = path.dirname(__file__)
    filepath = path.abspath(path.join(basepath, "..", "jira.yml"))
    print(filepath)
    with open(filepath) as file:
        dict= yaml.load(file, yaml.FullLoader)
    envSetting = dict['settings']['env']
    print(envSetting)

    hostname_port_var =envSetting['application_hostname'] + ':' + str(envSetting['application_port'])
    return hostname_port_var


HOSTNAME_PORT =get_hostname_port()


# get list of all users - except 'admin' if more than one user
print("hej")
print(HOSTNAME_PORT);
users_reponse = requests.get('http://'+ HOSTNAME_PORT  + '/rest/api/latest/user/search?username=.', auth=('admin', 'admin'))
assert users_reponse.status_code == 200
users = list(map(lambda user : user['name'], users_reponse.json()))
if len(users) > 1:
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
