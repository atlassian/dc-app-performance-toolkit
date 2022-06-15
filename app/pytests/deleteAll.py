import requests
import json
from fixtures import base_url
import os
from os import path
import pathlib

basepath = path.dirname(__file__)
#CURRENT_PATH = pathlib.Path().absolute()
delete_diagram_file_path = path.abspath(path.join(basepath, "deleteCreatedObjects"))

class TestDeleteAllDiagrams:
    def test_delete(self,  base_url):
        adminSession = requests.session()
        auth_response = adminSession.post(base_url + '/rest/auth/1/session',
                                          json={ "username": "admin", "password": "admin" })
        resp = adminSession.get(base_url + '/rest/api/2/project')
        assert resp.status_code == 200
        diagram_ids = []
        startAt=0
        while True:
            resp =adminSession.get(base_url + f'/rest/dependency-map/1.0/diagram?searchTerm=&startAt={startAt}&maxResults=50')
            assert resp.status_code == 200
            result = resp.json()
            if startAt >= result['total']  or not('values' in result):
                break
            diagram_ids.extend(list(map(lambda issue : issue['id'], result['values'])))
            startAt = len(diagram_ids)

        for diagram_id in  diagram_ids:
            deleteLine = "/rest/dependency-map/1.0/diagram/" + str(diagram_id)
            print(base_url + deleteLine)
            diagrams_response = adminSession.delete(base_url + deleteLine)
            print(diagrams_response)
