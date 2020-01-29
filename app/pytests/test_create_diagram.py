import requests
import json

#GET /rest/dependency-map/1.0/filter?
#       searchTerm=&page=0&resultsPerPage=25&_=1580224377777
#GET /rest/dependency-map/1.0/field?
#       searchTerm=&page=0&resultsPerPage=25&_=1580225386002
#GET /rest/dependency-map/1.0/user

#POST /rest/dependency-map/1.0/diagram
#POST /rest/dependency-map/1.0/linkConfig
#GET /plugins/servlet/dependency-map/diagram
#POST /rest/webResources/1.0/resources
#GET /rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50
#POST /rest/webResources/1.0/resources
#
#"GET /rest/hipchat/integrations/1.0/configuration/status?_=1580225581824
#"GET /rest/troubleshooting/1.0/check/admin?_=1580225581825
#GET /rest/api/2/filter/10001
#GET /rest/api/2/user?key=admin 
#POST /rest/analytics/1.0/publish/bulk

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
        
        payload ={ 'name':"D100", 'author':'admin', 
           'lastEditedBy':'admin', 'layoutId':0, 'filterKey': filterKey, 
            'boxColorFieldKey': field, 'groupedLayoutFieldKey': field, 
            'matrixLayoutHorizontalFieldKey': 'fixVersions', 'matrixLayoutVerticalFieldKey': 'fixVersions'}        
        
        print(payload);
        print(json.dumps(payload))
        diagrams_response = requests.post('http://localhost:8080/rest/dependency-map/1.0/diagram',           
            json=payload,
            cookies=dict(JSESSIONID=session_id))
        assert diagrams_response.status_code == 200
        print("Ny")
        print(diagrams_response.json())
               
        
 
