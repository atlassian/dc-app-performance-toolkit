import requests
from conftest import print_timing
from fixtures import session
from fixtures import base_url
import os
from maxfreq import max_freq
from conftest import print_in_shell
from conftest import getRandomFilter

class TestDelete:
    @max_freq(50/3600)
#    @print_timing
    def test_delete_diagram(self, base_url, session):
        # Prepare
        # request list of diagrams using the session id
        HOSTNAME = os.environ.get('application_hostname')
        diagrams_response = session.get('/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200

        # To make it thread save need to create the diagram before removing

        # Get user
        diagrams_response = session.get('/rest/dependency-map/1.0/user')
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]

        # Get filter key
        diagrams_response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
        assert diagrams_response.status_code == 200

        #Get filterKey randomly among the project in the project file
        filterKey= getRandomFilter(session)

        # Create diagram
        payload ={
          'name':"F100",
          'author':userKey,
          'layoutId':2,
          'filterKey': filterKey,
          'boxColorFieldKey': 'status',
          'groupedLayoutFieldKey': 'status',
          'matrixLayoutHorizontalFieldKey': 'status',
          'matrixLayoutVerticalFieldKey': 'priority',
          'showTypeIcons': True,
          'parallelIssueBatches': 4,
          'issuesPerRow': 5,
          'secondaryIssues': 1,
          'boxType': 0
        }

        diagrams_response = session.post('/rest/dependency-map/1.0/diagram',
                                         json=payload)
        assert diagrams_response.status_code == 200
        diagramId = diagrams_response.json()['id']

        #remove
        diagrams_response2 = session.delete('/rest/dependency-map/1.0/diagram/' + str(diagramId))
        assert diagrams_response2.status_code == 200
        print_in_shell("Diagram removed" +  str(diagramId))
        #print_in_shell( diagrams_response.json() );

        #get all diagrams after delete
        diagrams_response = session.get('/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200
