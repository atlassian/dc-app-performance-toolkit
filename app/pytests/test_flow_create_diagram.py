import requests
from conftest import print_timing
from fixtures import session
from fixtures import base_url
from conftest import saveRemoveDiagramCmd
import pytest
import time
import os
import random
from maxfreq import max_freq
from conftest import print_in_shell
from conftest import getRandomFilter
from conftest import getNrProjects

class TestFlowCreateDiagram:


    @max_freq(50/3600)
    @print_timing
    def test_create_diagram_flow_cd(self, base_url, session):


        #JIRA Get list of available link types
        HOSTNAME = os.environ.get('application_hostname')

        # Get field priority #
        diagrams_response = session.get('/rest/dependency-map/1.0/field/priority')
        assert diagrams_response.status_code == 200
        field = diagrams_response.json()["id"]

        # Get field option priority #
        diagrams_response = session.get('/rest/dependency-map/1.0/fieldOption/priority')
        assert diagrams_response.status_code == 200
        print(diagrams_response.json())

        # Get color palette entry#
        diagrams_response = session.get('/rest/dependency-map/1.0/colorPaletteEntry?palettId=' + '1')
        assert diagrams_response.status_code == 200

        # Get issue linktype #
        diagrams_response = session.get('/rest/api/2/issueLinkType')
        assert diagrams_response.status_code == 200

        # Get field #
        diagrams_response = session.get('/rest/api/2/field')
        assert diagrams_response.status_code == 200

        # Get field #
        diagrams_response = session.get('/rest/api/2/field')
        assert diagrams_response.status_code == 200

        # Get field fix version #
        diagrams_response = session.get('/rest/dependency-map/1.0/field/fixVersions')
        assert diagrams_response.status_code == 200
        field3 = diagrams_response.json()["id"]

        ############  Give name and select filter
        # Get filter
        diagrams_response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
        assert diagrams_response.status_code == 200

        # Get color palette entry#
        diagrams_response = session.get('/rest/dependency-map/1.0/colorPaletteEntry?palettId=' + '0')
        assert diagrams_response.status_code == 200

        # Get field priority , repeat this because if some other value was selected such a call had been made#
        diagrams_response = session.get('/rest/dependency-map/1.0/field/priority')
        assert diagrams_response.status_code == 200
        field = diagrams_response.json()["id"]

        # Get field option priority #
        diagrams_response = session.get('/rest/dependency-map/1.0/fieldOption/priority')
        assert diagrams_response.status_code == 200

        ############# Select issue color field
        # Get filter -
        diagrams_response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
        assert diagrams_response.status_code == 200

        #Get color palet entry
        diagrams_response = session.get('/rest/dependency-map/1.0/colorPaletteEntry?palettId=' + '0')
        assert diagrams_response.status_code == 200

        ############# Select Map layout matrix
        # Get field status
        diagrams_response = session.get('/rest/dependency-map/1.0/field/status')
        assert diagrams_response.status_code == 200
        field2 = diagrams_response.json()["id"]


        ############# Select filter
        # Get filter -
        diagrams_response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
        assert diagrams_response.status_code == 200

       ############## Select columns field
        # Get filter -
        diagrams_response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
        assert diagrams_response.status_code == 200

        ################ Create diagram #####################
        #Get filterKey randomly among the project in the project file
        filterKey= getRandomFilter(session)

        # Get user        
        diagrams_response = session.get('/rest/dependency-map/1.0/user')
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]
        
        # Create diagram
        payload = {'name': "F100", 'author': userKey,
                   'lastEditedBy': userKey, 'layoutId': 2, 'filterKey': filterKey,
                   'boxColorFieldKey': field, 'groupedLayoutFieldKey': field2,
                   'matrixLayoutHorizontalFieldKey': field2, 'matrixLayoutVerticalFieldKey': field3}
      
        diagrams_response = session.post('/rest/dependency-map/1.0/diagram',
            json=payload)
        assert diagrams_response.status_code == 200
        diagramId = diagrams_response.json()['id']
        guid = diagrams_response.json()['guid']
        diagramKey = str(diagramId)

        saveRemoveDiagramCmd(diagramId)

        #get diagram
        diagrams_response = session.get('/rest/dependency-map/1.0/diagram/' + diagramKey)

        ###### update issue colors

        # Get user
        diagrams_response = session.get('/rest/dependency-map/1.0/user')
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]

        #Update diagram
        payload = {'name': "F200", 'id': diagramId, 'author': userKey,
                   'lastEditedBy': userKey, 'layoutId': 2, 'filterKey': filterKey,
                   'boxColorFieldKey': field, 'groupedLayoutFieldKey': field2,
                   'matrixLayoutHorizontalFieldKey': field2, 'matrixLayoutVerticalFieldKey': field3,
                   'guid': guid}

        diagrams_response = session.put('/rest/dependency-map/1.0/diagram',
                                         json=payload)
        print(diagrams_response.json())
        assert diagrams_response.status_code == 200

        #create box colore resource entries.
        payload = {"diagramId":diagramId,"fieldId":"priority","fieldOptionId":1,"colorPaletteEntryId":5}
        diagrams_response = session.post('/rest/dependency-map/1.0/boxColor',
            json=payload)
        assert diagrams_response.status_code == 200

        payload = {"diagramId":diagramId,"fieldId":"priority","fieldOptionId":2,"colorPaletteEntryId":6}
        diagrams_response = session.post('/rest/dependency-map/1.0/boxColor',
                                     json=payload)
        assert diagrams_response.status_code == 200

        payload = {"diagramId":diagramId,"fieldId":"priority","fieldOptionId":3,"colorPaletteEntryId":7}
        diagrams_response = session.post('/rest/dependency-map/1.0/boxColor',
                                 json=payload)
        assert diagrams_response.status_code == 200

        payload = {"diagramId":diagramId,"fieldId":"priority","fieldOptionId":4,"colorPaletteEntryId":8}
        diagrams_response = session.post('/rest/dependency-map/1.0/boxColor',
                                 json=payload)
        assert diagrams_response.status_code == 200

        ###############Create link config entries
         # Get user
        diagrams_response = session.get('/rest/dependency-map/1.0/user')
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]

        #Update diagram
        payload = {'name': "F100", 'id': diagramId, 'author': userKey,
                   'lastEditedBy': userKey, 'layoutId': 2, 'filterKey': filterKey,
                   'boxColorFieldKey': field, 'groupedLayoutFieldKey': field2,
                   'matrixLayoutHorizontalFieldKey': field2, 'matrixLayoutVerticalFieldKey': field3,
                   'guid': guid}

        diagrams_response = session.put('/rest/dependency-map/1.0/diagram',
                                        json=payload)
        assert diagrams_response.status_code == 200

        #Get color palet entrie
        diagrams_response = session.get('/rest/dependency-map/1.0/colorPaletteEntry?paletteId=' + '1')
        assert diagrams_response.status_code == 200
        print(diagrams_response.json())

        colorPaletteEntryId = diagrams_response.json()[14]["id"]
        colorPaletteEntryId2 = diagrams_response.json()[10]["id"]
        colorPaletteEntryId3 = diagrams_response.json()[12]["id"]

        #Create linkConfig

        diagrams_response = session.get('/rest/api/2/issueLinkType')
        print(diagrams_response.json())
        issueLinkTypeIdStr = diagrams_response.json()['issueLinkTypes'][0]['id']
        issueLinkTypeId= int(issueLinkTypeIdStr)
        issueLinkTypeId2Str = diagrams_response.json()['issueLinkTypes'][1]['id']
        issueLinkTypeId2= int(issueLinkTypeId2Str)
        issueLinkTypeId3Str = diagrams_response.json()['issueLinkTypes'][2]['id']
        issueLinkTypeId3= int(issueLinkTypeId3Str)
        payload = { 'diagramId': diagramId, 'linkKey': issueLinkTypeId, 'visible': True , 'dashType': 0, 'width': 0, 'colorPaletteEntryId': colorPaletteEntryId}

        diagrams_response = session.post('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramKey,
                                         json=payload)
        assert(diagrams_response.status_code == 200)

        payload = { 'diagramId': diagramId, 'linkKey': issueLinkTypeId2, 'visible': True , 'dashType': 0, 'width': 0, 'colorPaletteEntryId': colorPaletteEntryId2}
        diagrams_response = session.post('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramKey,
                                         json=payload)
        assert(diagrams_response.status_code == 200)

        payload = { 'diagramId': diagramId, 'linkKey': issueLinkTypeId3, 'visible': True , 'dashType': 0, 'width': 0, 'colorPaletteEntryId': colorPaletteEntryId3}
        diagrams_response = session.post('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramKey,
                                         json=payload)
        assert(diagrams_response.status_code == 200)

        print("inside11")






        

        
             