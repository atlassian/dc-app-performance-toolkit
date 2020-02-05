import requests
import json
from fixtures import session

class TestCreateDiagram:
    def test_login(self, session):

        # Get filter key
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
        assert diagrams_response.status_code == 200
        filterKey= str(diagrams_response.json()["filters"][1]["filterKey"])
        print(filterKey)
        
        # Get field
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/field?searchTerm=&page=0&resultsPerPage=25')
        assert diagrams_response.status_code == 200
        field= diagrams_response.json()["fields"][0]["id"]
        print(field)

        # Get user        
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/user')
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]
        print(userKey)
        
        # Create diagram
        payload ={ 'name':"D100", 'author':'admin', 
           'lastEditedBy':'admin', 'layoutId':0, 'filterKey': filterKey, 
            'boxColorFieldKey': field, 'groupedLayoutFieldKey': field, 
            'matrixLayoutHorizontalFieldKey': 'fixVersions', 'matrixLayoutVerticalFieldKey': 'fixVersions'}               
      
        diagrams_response = session.post('http://localhost:8080/rest/dependency-map/1.0/diagram',
            json=payload)
        assert diagrams_response.status_code == 200
        print("Ny")
        print(diagrams_response.json())
               
        
 
