import requests
import json
from fixtures import base_url
import os
from os import path
import pathlib

basepath = path.dirname(__file__)
#CURRENT_PATH = pathlib.Path().absolute()
delete_diagram_file_path = path.abspath(path.join(basepath, "deleteCreatedObjects"))

class TestDelete:
    def test_delete(self,  base_url):
        print("BASE_URL: " + base_url)
        adminSession = requests.session()
        auth_response = adminSession.post(base_url + '/rest/auth/1/session',
                                          json={ "username": "admin", "password": "admin" })
        resp = adminSession.get(base_url + '/rest/api/2/project')
        assert resp.status_code == 200
        try:
            with open(delete_diagram_file_path) as f:
                for line in f:
                    deleteLine = line.strip();
                    print(base_url + deleteLine)
                    diagrams_response = adminSession.delete(base_url + deleteLine)
                    print(diagrams_response)
            f.close()
        except FileNotFoundError:
            print("File can not be found: " + str(delete_diagram_file_path))
        except:
            print("Something else went wrong")