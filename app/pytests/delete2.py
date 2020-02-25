import requests
import json
from fixtures import session
import os
import random
import pathlib
import json


HOSTNAME = os.environ.get('application_hostname')

CURRENT_PATH = pathlib.Path().absolute()
delete_diagram_file_path = CURRENT_PATH / "deleteCreatedObjects"

class TestDelete:
    def test_delete(self, session):
        HOSTNAME = os.environ.get('application_hostname')
       # diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50')
       # assert diagrams_response.status_code == 200
       # print(diagrams_response.json())
      #  diagrams = diagrams_response.json()['values']
      #  for diagram in diagrams :
      #      id = diagram['id']
      #      idString = str(id)
      #      diagram_response = session.delete('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram/' + idString)
       #     assert diagram_response.status_code == 200
       #     print("OK")

        diagram_ids = []
        diagram_ids_to_remove = []
        startAt = 0
        while True:
      #  resp = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50')
            resp = session.get('http://' + HOSTNAME + f':8080/rest/dependency-map/1.0/diagram?searchTerm=&startAt={startAt}&maxResults=50')
            assert resp.status_code == 200
            result = resp.json()
            if startAt >= result['total']:
                break
            diagram_ids.extend(list(map(lambda issue : issue['id'], result['values'])))
            startAt = len(diagram_ids)
            for value in result['values']:
                name = value["name"]

                if name in { "G100", "D100", "F100"}:
                   diagram_ids_to_remove.append(value['id'])

        print (diagram_ids_to_remove);

        for diagram_id in diagram_ids_to_remove:
            diagram_response = session.delete('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram/' + str(diagram_id))
            assert diagram_response.status_code == 200





        #
