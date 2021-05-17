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

class TestFlowCreateDiagram:

    @max_freq(50/3600)
    @print_timing
    def test_show_dependency_maps_flow_cd(self, base_url, session):

        #Select Dependency Map
        #GET /rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50 HTTP/1.1" 200 1630 3
        #GET /rest/api/2/filter/10000 HTTP/1.1" 200 631 2
        #GET /rest/api/2/filter/10001 HTTP/1.1" 200 632 2
        #GET /rest/api/2/user?key=admin HTTP/1.1" 200 344 1

        start = time.time()

        diagram_ids = []
        startAt = 0

        #Get all diagrams
        HOSTNAME = os.environ.get('application_hostname')
        while True:
            resp =session.get(f'/rest/dependency-map/1.0/diagram?searchTerm=&startAt={startAt}&maxResults=50')
            assert resp.status_code == 200
            result = resp.json()
            if startAt >= result['total'] or startAt > 500 or not('values' in result):
                break
            diagram_ids.extend(list(map(lambda issue : issue['id'], result['values'])))
            startAt = len(diagram_ids)
         #   print_in_shell(startAt)


        # Get filter key
        diagrams_response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
        assert diagrams_response.status_code == 200

        filterKey1=  getRandomFilter(session)
        filterKey2=  getRandomFilter(session)
        while filterKey1==filterKey2:
            filterKey2= getRandomFilter(session)

        # Get filter 10000  ?Scrum?
        diagrams_response = session.get('/rest/api/2/filter/' + filterKey1)
        assert diagrams_response.status_code == 200

        # Get filter 10001 ?Kanban?
        diagrams_response = session.get('/rest/api/2/filter/'+ filterKey2)
        assert diagrams_response.status_code == 200

        # Get user
        diagrams_response = session.get('/rest/dependency-map/1.0/user')
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]
        #print_in_shell(userKey)

    @max_freq(50/3600)
    @print_timing
    def test_create_diagram_flow_cd(self, base_url, session):
        # Create Diagram

        #JIRA Get list of available link types
        HOSTNAME = os.environ.get('application_hostname')
        diagrams_response = session.get('/rest/api/2/issueLinkType')
        assert diagrams_response.status_code == 200

        # Get filter key
        diagrams_response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
        assert diagrams_response.status_code == 200

        # Get filter key
        diagrams_response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
        assert diagrams_response.status_code == 200

        # Get filter key
        diagrams_response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
        assert diagrams_response.status_code == 200

        #Get filterKey randomly among the project in the project file
        filterKey= getRandomFilter(session)

        #Get color palet entry
        diagrams_response = session.get('/rest/dependency-map/1.0/colorPaletteEntry?paletteId=' + '1')
        assert diagrams_response.status_code == 200

        # Get field options - status
        diagrams_response = session.get('/rest/dependency-map/1.0/fieldOption/status')
        assert diagrams_response.status_code == 200

        #Get color palet entries
        diagrams_response = session.get('/rest/dependency-map/1.0/colorPaletteEntry?paletteId=' + '0')
        assert diagrams_response.status_code == 200

        # Get user
        diagrams_response = session.get('/rest/dependency-map/1.0/user')
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]

        # Create diagram
        payload ={
          'name': "A100",
          'layoutId': 2,
          'filterKey': filterKey,
          'boxColorFieldKey': 'priority',
          'groupedLayoutFieldKey': 'priority',
          'matrixLayoutHorizontalFieldKey': 'priority',
          'matrixLayoutVerticalFieldKey': 'priority',
          'showTypeIcons': True,
          'parallelIssueBatches': 4,
          'issuesPerRow': 5,
          'secondaryIssues': 1,
          'boxType': 0
        }

        diagrams_response = session.post('/rest/dependency-map/1.0/diagram',
            json=payload)
        assert diagrams_response.status_code == 200
        diagramId = diagrams_response.json()['id']
        diagramKey = str(diagramId)

        saveRemoveDiagramCmd(diagramId)

        #create box colore resource entries.
        payload = {"diagramId":diagramId,"fieldKey":"priority","fieldOptionId":1,"colorPaletteEntryId":5}
        diagrams_response = session.post('/rest/dependency-map/1.0/boxColor',
            json=payload)
        assert diagrams_response.status_code == 200

        payload = {"diagramId":diagramId,"fieldKey":"priority","fieldOptionId":2,"colorPaletteEntryId":6}
        diagrams_response = session.post('/rest/dependency-map/1.0/boxColor',
                                     json=payload)
        assert diagrams_response.status_code == 200

        payload = {"diagramId":diagramId,"fieldKey":"priority","fieldOptionId":3,"colorPaletteEntryId":7}
        diagrams_response = session.post('/rest/dependency-map/1.0/boxColor',
                                 json=payload)
        assert diagrams_response.status_code == 200

        payload = {"diagramId":diagramId,"fieldKey":"priority","fieldOptionId":4,"colorPaletteEntryId":8}
        diagrams_response = session.post('/rest/dependency-map/1.0/boxColor',
                                 json=payload)
        assert diagrams_response.status_code == 200

        #Create link config entries
        # Create linkConfig
        diagrams_response = session.get('/rest/api/2/issueLinkType')
        issueLinkTypeId = diagrams_response.json()['issueLinkTypes'][0]['id']

        issueLinkTypeId2 = diagrams_response.json()['issueLinkTypes'][1]['id']
        issueLinkTypeId3 = diagrams_response.json()['issueLinkTypes'][2]['id']

        payload = { 'diagramId': int(diagramKey), 'linkKey': int(issueLinkTypeId), 'visible': True, 'dashType': 0, 'width': 0, 'colorPaletteEntryId': 20}
        diagrams_response = session.post('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramKey,
                                         json=payload)
        assert(diagrams_response.status_code == 200)

        payload = { 'diagramId': int(diagramKey), 'linkKey': int(issueLinkTypeId2), 'visible': True, 'dashType': 0, 'width': 0, 'colorPaletteEntryId': 20}
        diagrams_response = session.post('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramKey,
                                        json=payload)

        assert(diagrams_response.status_code == 200)

        payload = { 'diagramId': int(diagramKey), 'linkKey': int(issueLinkTypeId3) , 'visible': True, 'dashType': 0, 'width': 0, 'colorPaletteEntryId': 20}
        diagrams_response = session.post('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramKey,
                                        json=payload)
        assert(diagrams_response.status_code == 200)
