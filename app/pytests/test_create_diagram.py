import requests
import json

class TestCreateDiagram:
    def test_login(self):
        # authenticate and get a session id
        auth_response = requests.post('http://localhost:8080/rest/auth/1/session',
            json={ "username": "admin", "password": "admin" })
        assert auth_response.status_code == 200
        session_id = auth_response.json()['session']['value']

        # Get filter key
        diagrams_response = requests.get('http://localhost:8080/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25',
            cookies=dict(JSESSIONID=session_id))
        assert diagrams_response.status_code == 200
        filterKey= str(diagrams_response.json()["filters"][1]["filterKey"])
        print(filterKey)
        
        # Get field
        diagrams_response = requests.get('http://localhost:8080/rest/dependency-map/1.0/field?searchTerm=&page=0&resultsPerPage=25',
            cookies=dict(JSESSIONID=session_id))
        assert diagrams_response.status_code == 200
        field= diagrams_response.json()["fields"][0]["id"]
        print(field)

        # Get user        
        diagrams_response = requests.get('http://localhost:8080/rest/dependency-map/1.0/user',
            cookies=dict(JSESSIONID=session_id))
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]
        print(userKey)
        
        # Create diagram
        payload ={ 'name':"D100", 'author':'admin', 
           'lastEditedBy':'admin', 'layoutId':0, 'filterKey': filterKey, 
            'boxColorFieldKey': field, 'groupedLayoutFieldKey': field, 
            'matrixLayoutHorizontalFieldKey': 'fixVersions', 'matrixLayoutVerticalFieldKey': 'fixVersions'}               
      
        diagrams_response = requests.post('http://localhost:8080/rest/dependency-map/1.0/diagram',           
            json=payload,
            cookies=dict(JSESSIONID=session_id))
        assert diagrams_response.status_code == 200
        print("Ny")
        print(diagrams_response.json())
               
        
 
