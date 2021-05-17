import requests
import json
from conftest import print_timing
from fixtures import session
from fixtures import base_url
from conftest import saveRemoveDiagramCmd
import os
from maxfreq import max_freq
from conftest import print_in_shell

class TestLinkConfig:
    @max_freq(500/3600)
    @print_timing
    def test_create_change_link(self, base_url, session):
        HOSTNAME = os.environ.get('application_hostname')
        # Get user
        diagrams_response = session.get('/rest/dependency-map/1.0/user')
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]
        print_in_shell("User key: " + userKey)

        # Create diagram
        payload = {
          'name':"E100",
          'layoutId':0,
          'filterKey': 10000,
          'boxColorFieldKey': "priority",
          'groupedLayoutFieldKey': "priority",
          'matrixLayoutHorizontalFieldKey': 'fixVersions',
          'matrixLayoutVerticalFieldKey': 'fixVersions',
          'showTypeIcons': True,
          'parallelIssueBatches': 4,
          'issuesPerRow': 5,
          'secondaryIssues': 1,
          'boxType': 0
        }
        diagrams_response = session.post('/rest/dependency-map/1.0/diagram',
            json=payload)

        newDiagram = diagrams_response.json()
        print('newDiagram=', newDiagram)
        diagramId = str(newDiagram["id"])
        saveRemoveDiagramCmd(diagramId)

        #JIRA Get list of available link types
        diagrams_response = session.get('/rest/api/2/issueLinkType')
        issueLinkTypeId = diagrams_response.json()['issueLinkTypes'][0]['id']
        print_in_shell("issueLinkTypeId=" + issueLinkTypeId)
        print_in_shell( diagrams_response.json() )

        # Get all link configs
        diagrams_response = session.get('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId)
        print_in_shell("all link configs")
        print_in_shell( diagrams_response.json() )

        # Create linkConfig
        payload = { 'diagramId': diagramId, 'linkKey': 10000, 'visible': True, 'dashType': 0, 'width': 0, 'colorPaletteEntryId': 20}

        diagrams_response = session.post('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId,
            json=payload)

        newLinkConfig = diagrams_response.json()
        print('newLinkConfig=', newLinkConfig)
        assert(diagrams_response.status_code == 200)

        # Update linkConfig
        payload = {'diagramId': diagramId, 'linkKey': 10000, 'visible': True, 'dashType': 1, 'width': 2, 'colorPaletteEntryId': 39}

        diagrams_response = session.post('/rest/dependency-map/1.0/linkConfig',
            json=payload)
        assert(diagrams_response.status_code == 200)

        # Get all link configs
        diagrams_response = session.get('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId)
        print_in_shell( diagrams_response.json() )
