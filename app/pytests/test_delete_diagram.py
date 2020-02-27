import requests
from conftest import print_timing
from fixtures import session
import os
from maxfreq import max_freq

class TestDelete:
  #  @max_freq(50/3600)
    @print_timing
    def test_delete_diagram(self, session):
        # Prepare
        # request list of diagrams using the session id
        HOSTNAME = os.environ.get('application_hostname')
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200
        total = diagrams_response.json()["total"];
        values = diagrams_response.json()["values"];
        diagram1 = values[0];
        id1= diagram1["id"]
        idString = str(id1)

        # To make it thread save need to create the diagram before removing

        # Get user
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/user')
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]

        # Get filter key
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
        assert diagrams_response.status_code == 200

        filterKey= str(diagrams_response.json()["filters"][0]["filterKey"])

        # Get field status
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/field/status')
        assert diagrams_response.status_code == 200
        field= diagrams_response.json()["id"]

        # Get field sprint
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/field/sprint')
        assert diagrams_response.status_code == 200
        field2= diagrams_response.json()["id"]

        # Create diagram
        payload ={ 'name':"F100", 'author':userKey,
                   'lastEditedBy':userKey, 'layoutId':2, 'filterKey': filterKey,
                   'boxColorFieldKey': field, 'groupedLayoutFieldKey': field,
                   'matrixLayoutHorizontalFieldKey': field, 'matrixLayoutVerticalFieldKey': field2}

        diagrams_response = session.post('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram',
                                         json=payload)
        assert diagrams_response.status_code == 200
        diagramId = diagrams_response.json()['id']

        #remove
        diagrams_response2 = session.delete('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram/' + str(diagramId))
        assert diagrams_response2.status_code == 200
        print("Diagram removed")
        #print( diagrams_response.json() );

        #get all diagrams after delete
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200

        
 
