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
    @print_timing
    def test_delete_diagram(self, base_url, session):
        # Prepare
        # request list of diagrams using the session id
        HOSTNAME = os.environ.get('application_hostname')

        ##CREATE DIAGRAM
        # Get user
        diagrams_response = session.get('/rest/dependency-map/1.0/user')
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]

        # Get filter key
        diagrams_response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
        assert diagrams_response.status_code == 200

        # Get field status
        diagrams_response = session.get('/rest/dependency-map/1.0/field/status')
        assert diagrams_response.status_code == 200
        field= diagrams_response.json()["id"]

        # Get field priority
        diagrams_response = session.get('/rest/dependency-map/1.0/field/priority')
        assert diagrams_response.status_code == 200
        field2= diagrams_response.json()["id"]

        #Get filterKey randomly among the project in the project file
        filterKey= getRandomFilter(session)

        # Create diagram
        payload ={ 'name':"F100", 'author':userKey,
                   'lastEditedBy':userKey, 'layoutId':2, 'filterKey': filterKey,
                   'boxColorFieldKey': field, 'groupedLayoutFieldKey': field,
                   'matrixLayoutHorizontalFieldKey': field, 'matrixLayoutVerticalFieldKey': field2}

        diagrams_response = session.post('/rest/dependency-map/1.0/diagram',
                                         json=payload)
        assert diagrams_response.status_code == 200
        diagramId = diagrams_response.json()['id']

        print("Hej")

        ##FIND DIAGRAM

        # To make it thread save need to create the diagram before removing
        # Get user
        diagrams_response = session.get('/rest/dependency-map/1.0/user')
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]

        # Get filter key
        diagrams_response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
        assert diagrams_response.status_code == 200


        #Get favoritDiagram
        diagrams_response = session.get('/rest/dependency-map/1.0/favoriteDiagram')
        assert diagrams_response.status_code == 200

        #Get diagrams with filterKey
        diagrams_response = session.get('/rest/dependency-map/1.0/diagram?filterKey=' + filterKey + '&searchTerm=&sortBy=name&reverseSort=&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200

     #   #Get filter
        diagrams_response = session.get('/rest/api/2/filter/' + filterKey)
        assert diagrams_response.status_code == 200

        #Get diagram
        diagrams_response = session.get('/rest/dependency-map/1.0/diagram/' + str(diagramId))
        assert diagrams_response.status_code == 200

        ##REMOVE
        #remove
        diagrams_response2 = session.delete('/rest/dependency-map/1.0/diagram/' + str(diagramId))
        assert diagrams_response2.status_code == 200
        print_in_shell("Diagram removed" +  str(diagramId))
        #print_in_shell( diagrams_response.json() );

        #get all diagrams after delete
        diagrams_response = session.get('/rest/dependency-map/1.0/diagram?filterKey=' + filterKey + '&searchTerm=&sortBy=name&reverseSort=&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200

        
 
