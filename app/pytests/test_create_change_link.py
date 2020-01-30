import requests
import json

class TestCreateChangeLink:
    def test_create_change_link(self):
        # authenticate and get a session id
        auth_response = requests.post('http://localhost:8080/rest/auth/1/session',
            json={ "username": "admin", "password": "admin" })
        assert auth_response.status_code == 200
        session_id = auth_response.json()['session']['value']

        
        # Create diagram
        payload ={ 'name':"D100", 'author':'admin', 
           'lastEditedBy':'admin', 'layoutId':0, 'filterKey': 10000, 
            'boxColorFieldKey': "priority", 'groupedLayoutFieldKey': "priority", 
            'matrixLayoutHorizontalFieldKey': 'fixVersions', 'matrixLayoutVerticalFieldKey': 'fixVersions'}        
            
        diagrams_response = requests.post('http://localhost:8080/rest/dependency-map/1.0/diagram',           
            json=payload,
            cookies=dict(JSESSIONID=session_id))
            
        print( diagrams_response.json() )
        newDiagram = diagrams_response.json()
        diagramId = str(newDiagram["id"])
        print(diagramId)
        
        # Get all link configs
        diagrams_response = requests.get('http://localhost:8080/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId,           
            cookies=dict(JSESSIONID=session_id))
        print( diagrams_response.json() )  
        
        # Create linkConfig
        payload = { 'diagramId': diagramId, 'linkKey': 10000, 'visible': True, 'dashType': 0, 'width': 0, 'colorPaletteEntryId': 20}      
        
        diagrams_response = requests.post('http://localhost:8080/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId,           
            json=payload,
            cookies=dict(JSESSIONID=session_id))
        
        newLinkConfig = diagrams_response.json()
        linkConfigId = str(newLinkConfig["id"])
        print(linkConfigId)             		            
        assert(diagrams_response.status_code == 200)
        
        # Update linkConfig         
        payload = { 'id': linkConfigId, 'diagramId': diagramId, 'linkKey': 10000, 'visible': True, 'dashType': 1, 'width': 2, 'colorPaletteEntryId': 39}      
        
        diagrams_response = requests.put('http://localhost:8080/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId,           
            json=payload,
            cookies=dict(JSESSIONID=session_id))
        assert(diagrams_response.status_code == 200)
        
        # Get all link configs
        diagrams_response = requests.get('http://localhost:8080/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId,           
            cookies=dict(JSESSIONID=session_id))
        print( diagrams_response.json() ) 
           
        
        
              
        
 
