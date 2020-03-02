import requests
from conftest import print_timing
from fixtures import session
from conftest import saveRemoveDiagramCmd
import os
import random
import pathlib
from maxfreq import max_freq

class TestCopyDiagram:
    @max_freq(50/3600)
    @print_timing
    def test_copy_diagram(self, session):
        HOSTNAME = os.environ.get('application_hostname')

        #create a copy of the diagram
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200
        result = diagrams_response.json()['values']
        diagramId=result[0]['id']

        #create a copy of the diagram
        diagrams_response = session.post('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram/duplicate/' + str(diagramId) )
        assert diagrams_response.status_code == 200

        diagramId = diagrams_response.json()['diagram']['id']
        saveRemoveDiagramCmd(diagramId)

