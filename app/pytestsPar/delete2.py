import requests
import json
from fixtures import base_url
import os
import random
import pathlib
import json




CURRENT_PATH = pathlib.Path().absolute()
delete_diagram_file_path = CURRENT_PATH / "deleteCreatedObjects"

class TestDelete:
    def test_delete_diagrams(self, base_url):
       # diagrams_response = session.get('/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50')
       # assert diagrams_response.status_code == 200
       # print(diagrams_response.json())
      #  diagrams = diagrams_response.json()['values']
      #  for diagram in diagrams :
      #      id = diagram['id']
      #      idString = str(id)
      #      diagram_response = session.delete('/rest/dependency-map/1.0/diagram/' + idString)
       #     assert diagram_response.status_code == 200
       #     print("OK")

        diagram_ids = []
        diagram_ids_to_remove = []
        startAt = 0
        adminSession = requests.session()
        auth_response = adminSession.post(base_url + '/rest/auth/1/session',
                                         json={ "username": "admin", "password": "admin" })
        while True:
            resp = adminSession.get( base_url + f'/rest/dependency-map/1.0/diagram?searchTerm=&startAt={startAt}&maxResults=50')
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
            diagram_response = adminSession.delete(base_url + '/rest/dependency-map/1.0/diagram/' + str(diagram_id))
            assert diagram_response.status_code == 200
            print("Diagram removed")

    def test_delete_issues(self, base_url):
        adminSession = requests.session()
        auth_response = adminSession.post(base_url + '/rest/auth/1/session',
                                          json={ "username": "admin", "password": "admin" })
        resp = adminSession.get(base_url + '/rest/api/2/project')
        assert resp.status_code == 200

        for project in resp.json():
            project_key = project['key']
            # collect keys of all issues in this project into issue_ids
            link_percentage = 30
            issue_ids = []
            issue_keys_to_delete = []
            startAt = 0
            while True:
                resp = adminSession.get(base_url + f'/rest/api/latest/search?maxResults=2&startAt={startAt}&jql=project={project_key}&fields=key')
                assert resp.status_code == 200
                result = resp.json()
                if startAt >= result['total']:
                    break
                issue_ids.extend(list(map(lambda issue : issue['id'], result['issues'])))
                startAt = len(issue_ids)

                for issue in result['issues']:
                    print(issue['key'])
                    issue_keys_to_delete.append(issue['key'])

            print(issue_keys_to_delete)
            for issue_key in issue_keys_to_delete:   #issue_ids:
                print('/rest/api/2/issue/' +  issue_key);

                diagrams_response = ""
                try:
                    diagrams_response = adminSession.delete(base_url +'/rest/api/2/issue/' +  issue_key)
                    print( diagrams_response )
                    assert diagrams_response.status_code == 204
                except:
                    print( diagrams_response.json() )






        #
