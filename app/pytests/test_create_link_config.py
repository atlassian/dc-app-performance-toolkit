import requests
import json
from fixtures import session
import os

class TestLinkConfig:
    def test_create_change_link(self, session):
        # Create diagram
        payload ={ 'name':"D100", 'author':'admin', 
           'lastEditedBy':'admin', 'layoutId':0, 'filterKey': 10000, 
            'boxColorFieldKey': "priority", 'groupedLayoutFieldKey': "priority", 
            'matrixLayoutHorizontalFieldKey': 'fixVersions', 'matrixLayoutVerticalFieldKey': 'fixVersions'}
        HOSTNAME = os.environ.get('application_hostname')
        diagrams_response = session.post('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram',
            json=payload)

        newDiagram = diagrams_response.json()
        diagramId = str(newDiagram["id"])
        print("New diagram id: " + diagramId)

        #JIRA Get list of available link types
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/api/2/issueLinkType')
        issueLinkTypeId = diagrams_response.json()['issueLinkTypes'][0]['id']
        print("issueLinkTypeId=" + issueLinkTypeId)
        print( diagrams_response.json() )
        
        # Get all link configs
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId)
        print("all link configs")
        print( diagrams_response.json() )  
        
        # Create linkConfig
        payload = { 'diagramId': diagramId, 'linkKey': 10000, 'visible': True, 'dashType': 0, 'width': 0, 'colorPaletteEntryId': 20}      
        
        diagrams_response = session.post('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId,
            json=payload)
        
        newLinkConfig = diagrams_response.json()
        linkConfigId = str(newLinkConfig["id"])
        print(linkConfigId)             		            
        assert(diagrams_response.status_code == 200)
        
        # Update linkConfig         
        payload = { 'id': linkConfigId, 'diagramId': diagramId, 'linkKey': 10000, 'visible': True, 'dashType': 1, 'width': 2, 'colorPaletteEntryId': 39}      
        
        diagrams_response = session.put('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId,
            json=payload)
        assert(diagrams_response.status_code == 200)
        
        # Get all link configs
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId)
        print( diagrams_response.json() ) 
           
        
        
              
        
 
