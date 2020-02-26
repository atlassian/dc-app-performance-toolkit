import pytest
import requests
import os
import random
import time
import pathlib

HOSTNAME = os.environ.get('application_hostname')
CURRENT_PATH = pathlib.Path().absolute()
out_file_path = CURRENT_PATH / "deleteCreatedObjects"

# get list of all users - except 'admin' if more than one user
users_reponse = requests.get('http://' + HOSTNAME + ':8080/rest/api/latest/user/search?username=.', auth=('admin', 'admin'))
assert users_reponse.status_code == 200
users = list(map(lambda user : user['name'], users_reponse.json()))
if len(users) > 1:
    users.remove('admin')
print(users)

def saveRemoveDiagramCmd(diagramId):
    try:
        with open(out_file_path, "a") as f:
            diagrams_delete_request ='http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram/' + str(diagramId)
            f.write(diagrams_delete_request)
            f.write("\n")
            f.close()
    except IOError:
        print("File not accessible" + diagramId)

def saveRemoveIssueLinkCmd(issueLinkId):
    try:
        with open(out_file_path, "a") as f:
            issueLink_delete_request ='http://'  + HOSTNAME + ':8080/rest/api/latest/issueLink/' + str(issueLinkId)
            f.write(issueLink_delete_request)
            f.write("\n")
            f.close()
    except IOError:
        print("File not accessible" + issueLinkId)

# returns a random username/password dict
# all users have password 'password', except user 'admin' that has password 'admin'
def getRandomUsernamePassword():
    username = random.choice(users)
    password = 'password'
    if username == 'admin':
        password = 'admin'
    print(username)
    print("RETURN USER: " + username)
    return {'username': username, 'password': password}

# returns a logged in session for use in a test method
@pytest.fixture(scope="class")
def session():
 #   time.sleep(20)
    print("create session")
    # authenticate to get a session id
    s = requests.session()
    auth_response = s.post('http://' + HOSTNAME + ':8080/rest/auth/1/session',
                           json=getRandomUsernamePassword())

    # after test teardown
    yield s  # provide the fixture value
    print("teardown session")
    s.close()
    return s
