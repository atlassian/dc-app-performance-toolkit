import requests
import json
from fixtures import session

class TestCreateDiagram:
    def test_create_diagram(self, session):

    #GET /rest/api/2/issueLinkType HTTP/1.1" 200 229 3 "http://localhost:8080/plugins/servlet/dependency-map/diagram" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) A
    #GET /rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25&_=1580893219884 HTTP/1.1" 200 153 2 "http://localhost:8080/plugins/servlet/dependenc
    #GET /rest/dependency-map/1.0/field?searchTerm=&page=0&resultsPerPage=25&_=1580893250444 HTTP/1.1" 200 243 1 "http://localhost:8080/plugins/servlet/dependency
    #GET /rest/dependency-map/1.0/field?searchTerm=&page=0&resultsPerPage=25&_=1580893254366 HTTP/1.1" 200 243 1 "http://localhost:8080/plugins/servlet/dependency
    #GET /rest/dependency-map/1.0/user HTTP/1.1" 200 96 1 "http://localhost:8080/plugins/servlet/dependency-map/diagram" "Mozilla/5.0 (Windows NT 10.0; Win64; x64
    #POST /rest/dependency-map/1.0/diagram HTTP/1.1" 200 226 2 "http://localhost:8080/plugins/servlet/dependency-map/diagram" "Mozilla/5.0 (Windows NT 10.0; Win64
    #POST /rest/dependency-map/1.0/linkConfig HTTP/1.1" 200 134 5 "http://localhost:8080/plugins/servlet/dependency-map/diagram" "Mozilla/5.0 (Windows NT 10.0; Wi

    # ??? POST /rest/webResources/1.0/resources HTTP/1.1" 200 494 3 "http://localhost:8080/plugins/servlet/dependency-map/diagram" "Mozilla/5.0 (Windows NT 10.0; Win64

    #GET /rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50 HTTP/1.1" 200 960 3 "http://localhost:8080/plugins/servlet/dependency-map/diagram" "

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

       # Get field
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/field?searchTerm=&page=0&resultsPerPage=25')
        assert diagrams_response.status_code == 200
        field= diagrams_response.json()["fields"][0]["id"]
        print(field)

        # Get user        
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/user')
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]
        print("User key: " + userKey)
        
        # Create diagram
        payload ={ 'name':"D100", 'author':'admin', 
           'lastEditedBy':'admin', 'layoutId':0, 'filterKey': filterKey, 
            'boxColorFieldKey': field, 'groupedLayoutFieldKey': field, 
            'matrixLayoutHorizontalFieldKey': 'fixVersions', 'matrixLayoutVerticalFieldKey': 'fixVersions'}               
      
        diagram_response = session.post('http://localhost:8080/rest/dependency-map/1.0/diagram',
            json=payload)
        assert diagram_response.status_code == 200
        diagramId = str(diagram_response.json()["id"])
        print("New diagram id: " + diagramId)

        # Create linkConfig
        payload = { 'diagramId': diagramId, 'linkKey': 10000, 'visible': True, 'dashType': 0, 'width': 0, 'colorPaletteEntryId': 20}

        diagrams_response = session.post('http://localhost:8080/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId,
            json=payload)

        newLinkConfig = diagrams_response.json()
        linkConfigId = str(newLinkConfig["id"])
        print(linkConfigId)
        assert(diagrams_response.status_code == 200)

        # Get diagrams
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200

