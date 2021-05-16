import requests
from conftest import print_timing
from fixtures import session
from fixtures import base_url
from conftest import saveRemoveDiagramCmd
from conftest import getRandomFilter
import os
import random
import pathlib
from maxfreq import max_freq

class TestCopyDiagram:
    @max_freq(50/3600)
    @print_timing
    def test_copy_diagram(self, base_url, session):
        HOSTNAME = os.environ.get('application_hostname')

        #Get filterKey randomly among the project in the project file
        filterKey= getRandomFilter(session)

        diagrams_response = session.get('/rest/dependency-map/1.0/diagram?filterKey=' + filterKey + '&searchTerm=&sortBy=name&reverseSort=&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200
        result = diagrams_response.json()['values']
        if len(result)>0:
            diagramId=result[0]['id']

            #create a copy of the diagram
            diagrams_response = session.post('/rest/dependency-map/1.0/diagram/duplicate/' + str(diagramId) )
            assert diagrams_response.status_code == 200

            diagramId = diagrams_response.json()['diagram']['id']
            saveRemoveDiagramCmd(diagramId)

