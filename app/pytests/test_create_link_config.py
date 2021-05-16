import requests
import json
from conftest import print_timing
from fixtures import session
from fixtures import base_url
from conftest import getRandomProjectId
from conftest import saveRemoveDiagramCmd
from conftest import getFilterId
import os
from maxfreq import max_freq
from conftest import print_in_shell

def get_link_type(session):
    #JIRA Get list of available link types
    HOSTNAME = os.environ.get('application_hostname')
    issueLinkTypeId = 0
    diagrams_response = session.get('/rest/api/2/issueLinkType')
    issueLinkTypes = diagrams_response.json()['issueLinkTypes']
    for linkType in issueLinkTypes:
        print_in_shell(linkType)
        if linkType["name"]=="Blocks":
            issueLinkTypeId=linkType["id"]
            break
    print_in_shell(issueLinkTypeId)
    return issueLinkTypeId

class TestLinkConfig:

    @max_freq(500/3600)
    @print_timing
    def test_create_change_link(self, base_url, session):
        # Get project and filter  id from the list of projects we shall use, saved in a file
        projectId=getRandomProjectId()
        filterId = getFilterId(projectId)

        # Get user
        diagrams_response = session.get('/rest/dependency-map/1.0/user')
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]
        print_in_shell("User key: " + userKey)

        # Create diagram
        payload ={ 'name':"E100", 'author': userKey,
           'lastEditedBy':userKey, 'layoutId':0, 'filterKey': filterId,
            'boxColorFieldKey': "priority", 'groupedLayoutFieldKey': "priority", 
            'matrixLayoutHorizontalFieldKey': 'fixVersions', 'matrixLayoutVerticalFieldKey': 'fixVersions'}
        diagrams_response = session.post('/rest/dependency-map/1.0/diagram',
            json=payload)

        newDiagram = diagrams_response.json()
        diagramId = str(newDiagram["id"])
        saveRemoveDiagramCmd(diagramId)

        issueLinkTypeId= get_link_type(session)
        print(issueLinkTypeId)
        
        # Get all link configs
        #diagrams_response = session.get('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId)
        #print_in_shell("all link configs")
        #print_in_shell( diagrams_response.json() )
        
        # Create linkConfig
        payload = { 'diagramId': diagramId, 'linkKey': issueLinkTypeId, 'visible': True, 'dashType': 0, 'width': 0, 'colorPaletteEntryId': 20}
        
        diagrams_response = session.post('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId,
            json=payload)
        
        newLinkConfig = diagrams_response.json()
        linkConfigId = str(newLinkConfig["id"])
        print_in_shell(linkConfigId)
        assert(diagrams_response.status_code == 200)
        
        # Update linkConfig         
        payload = { 'id': linkConfigId, 'diagramId': diagramId, 'linkKey': issueLinkTypeId, 'visible': True, 'dashType': 1, 'width': 2, 'colorPaletteEntryId': 39}
        
        diagrams_response = session.put('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId,
            json=payload)
        assert(diagrams_response.status_code == 200)
        
        # Get all link configs
        diagrams_response = session.get('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId)
        print_in_shell( diagrams_response.json() )
           
        
        
              
        
 
