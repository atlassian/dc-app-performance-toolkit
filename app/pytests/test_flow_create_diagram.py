import requests
from fixtures import session
import time
import os

class TestFlowCreateDiagram:


    def test_show_dependency_maps_flow_cd(self, session):
        #Select Dependency Map
        #GET /rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50 HTTP/1.1" 200 1630 3
        #GET /rest/api/2/filter/10000 HTTP/1.1" 200 631 2
        #GET /rest/api/2/filter/10001 HTTP/1.1" 200 632 2
        #GET /rest/api/2/user?key=admin HTTP/1.1" 200 344 1

        start = time.time()
        #Get all diagrams
        HOSTNAME = os.environ.get('application_hostname')
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200

        # Get filter 10000  Scrum
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/api/2/filter/10000')
        assert diagrams_response.status_code == 200

        # Get filter 10001 Kanban
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/api/2/filter/10001')
        assert diagrams_response.status_code == 200

        # Get user
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/user')
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]
        #print(userKey)


    def test_create_diagram_flow_cd(self, session):
        # Create Diagram
        #GET /rest/api/2/issueLinkType HTTP/1.1" 200 229 2
        #GET /rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25&_=1580998061249 HTTP/1.1" 200 153 4
        #GET /rest/dependency-map/1.0/field?searchTerm=&page=0&resultsPerPage=25&_=1580998098959 HTTP/1.1" 200 243 2
        #GET /rest/dependency-map/1.0/field?searchTerm=&page=0&resultsPerPage=25&_=1580998107182 HTTP/1.1" 200 243 3
        #GET /rest/dependency-map/1.0/colorPaletteEntry?paletteId=1 HTTP/1.1" 200 295 1
        #GET /rest/dependency-map/1.0/field/status HTTP/1.1" 200 68 1
        #GET /rest/dependency-map/1.0/fieldOption/status HTTP/1.1" 200 201 1
        #GET /rest/dependency-map/1.0/colorPaletteEntry?paletteId=0 HTTP/1.1" 200 287 1
        #GET /rest/dependency-map/1.0/user HTTP/1.1" 200 96 1

        # POST /rest/dependency-map/1.0/diagram HTTP/1.1" 200 226 2
        # POST /rest/dependency-map/1.0/boxColor HTTP/1.1" 200 118 11
        # POST /rest/dependency-map/1.0/boxColor HTTP/1.1" 200 117 11
        # POST /rest/dependency-map/1.0/boxColor HTTP/1.1" 200 119 9
        # POST /rest/dependency-map/1.0/boxColor HTTP/1.1" 200 119 9
        # POST /rest/dependency-map/1.0/linkConfig HTTP/1.1" 200 137 2
        # POST /rest/dependency-map/1.0/linkConfig HTTP/1.1" 200 137 3
        # POST /rest/dependency-map/1.0/linkConfig HTTP/1.1" 200 137 3
        # POST /rest/dependency-map/1.0/linkConfig HTTP/1.1" 200 139 3
        # POST /rest/dependency-map/1.0/linkConfig HTTP/1.1" 200 133 7
        # POST /rest/dependency-map/1.0/linkConfig HTTP/1.1" 200 137 12

        # GET /rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50 HTTP/1.1" 200 1620 4 "http://'  + HOSTNAME + ':8080/plugins/servlet/depen
        # POST /rest/webResources/1.0/resources HTTP/1.1" 200 86 3 "http://'  + HOSTNAME + ':8080/plugins/servlet/dependency-map/diagram" "Mozilla/5.0 (

        # GET /rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50 HTTP/1.1" 200 1620 4 "http://'  + HOSTNAME + ':8080/plugins/servlet/depen
        # GET /rest/api/2/filter/10000 HTTP/1.1" 200 631 3 "http://'  + HOSTNAME + ':8080/plugins/servlet/dependency-map/diagram" "Mozilla/5.0 (Windows NT 1
        # GET /rest/api/2/user?key=admin HTTP/1.1" 200 344 2 "http://'  + HOSTNAME + ':8080/plugins/servlet/dependency-map/diagram" "Mozilla/5.0 (Windows NT


        #JIRA Get list of available link types
        HOSTNAME = os.environ.get('application_hostname')
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/api/2/issueLinkType')
        assert diagrams_response.status_code == 200

        # Get filter key
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
        assert diagrams_response.status_code == 200

        # Get filter key
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
        assert diagrams_response.status_code == 200
        filterKey= str(diagrams_response.json()["filters"][1]["filterKey"])

        # Get filter key
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
        assert diagrams_response.status_code == 200

        #Get color palet entry
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/colorPaletteEntry?palettId=' + '1')
        assert diagrams_response.status_code == 200
        
        # Get field status
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/field/status')
        assert diagrams_response.status_code == 200
        field= diagrams_response.json()["id"]

        # Get field options - status
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/fieldOption/status')
        assert diagrams_response.status_code == 200

        #Get color palet entries
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/colorPaletteEntry?palettId=' + '0')
        assert diagrams_response.status_code == 200

        # Get user        
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/user')
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]
        
        # Create diagram
        payload ={ 'name':"F100", 'author':'admin',
           'lastEditedBy':'admin', 'layoutId':0, 'filterKey': filterKey, 
            'boxColorFieldKey': field, 'groupedLayoutFieldKey': field, 
            'matrixLayoutHorizontalFieldKey': 'fixVersions', 'matrixLayoutVerticalFieldKey': 'fixVersions'}               
      
        diagrams_response = session.post('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram',
            json=payload)
        assert diagrams_response.status_code == 200
        diagramId = diagrams_response.json()['id']
        diagramKey = str(diagramId)
        
        #create box colore resource entries.
        payload = {"diagramId":diagramId,"fieldId":"priority","fieldOptionId":1,"colorPaletteEntryId":5}
        diagrams_response = session.post('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor',
            json=payload)
        assert diagrams_response.status_code == 200

        payload = {"diagramId":diagramId,"fieldId":"priority","fieldOptionId":2,"colorPaletteEntryId":6}
        diagrams_response = session.post('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor',
                                     json=payload)
        assert diagrams_response.status_code == 200

        payload = {"diagramId":diagramId,"fieldId":"priority","fieldOptionId":3,"colorPaletteEntryId":7}
        diagrams_response = session.post('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor',
                                 json=payload)
        assert diagrams_response.status_code == 200

        payload = {"diagramId":diagramId,"fieldId":"priority","fieldOptionId":4,"colorPaletteEntryId":8}
        diagrams_response = session.post('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor',
                                 json=payload)
        assert diagrams_response.status_code == 200

        #Create link config entries
        # Create linkConfig
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/api/2/issueLinkType')
        issueLinkTypeId = diagrams_response.json()['issueLinkTypes'][0]['id']

        issueLinkTypeId2 = diagrams_response.json()['issueLinkTypes'][1]['id']
        issueLinkTypeId3 = diagrams_response.json()['issueLinkTypes'][2]['id']

        payload = { 'diagramId': diagramKey, 'linkKey': issueLinkTypeId, 'visible': True, 'dashType': 0, 'width': 0, 'colorPaletteEntryId': 5}
        diagrams_response = session.post('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramKey,
                                         json=payload)
        assert(diagrams_response.status_code == 200)

        payload = { 'diagramId': diagramKey, 'linkKey': issueLinkTypeId2, 'visible': True, 'dashType': 0, 'width': 0, 'colorPaletteEntryId': 6}
        diagrams_response = session.post('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramKey,
                                        json=payload)
        assert(diagrams_response.status_code == 200)

        payload = { 'diagramId': diagramKey, 'linkKey': issueLinkTypeId3 , 'visible': True, 'dashType': 0, 'width': 0, 'colorPaletteEntryId': 1}
        diagrams_response = session.post('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramKey,
                                        json=payload)
        assert(diagrams_response.status_code == 200)






        

        
             