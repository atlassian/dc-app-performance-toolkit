import requests
import json
from fixtures import session
import os
import random
import pathlib


HOSTNAME = os.environ.get('application_hostname')

CURRENT_PATH = pathlib.Path().absolute()
delete_diagram_file_path = CURRENT_PATH / "deleteCreatedObjects"

class TestDelete:
    def test_delete(self, session):
        HOSTNAME = os.environ.get('application_hostname')
        adminSession = requests.session()
        auth_response = adminSession.post('http://' + HOSTNAME + ':8080/rest/auth/1/session',
                                          json={ "username": "admin", "password": "admin" })
        resp = adminSession.get('http://'  + HOSTNAME + ':8080/rest/api/2/project')
        assert resp.status_code == 200
        with open(delete_diagram_file_path) as f:
            for line in f:
                print("Line:" + line);
                deleteLine = line.strip();
                print(deleteLine)
                diagrams_response = adminSession.delete(deleteLine)
                print(diagrams_response)
        f.close()