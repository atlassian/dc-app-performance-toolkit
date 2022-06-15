import requests
import json
from conftest import print_timing
from fixtures import session
from fixtures import base_url
from conftest import saveRemoveDiagramCmd
from conftest import print_in_shell

import os
from maxfreq import max_freq
import pathlib
import pytest

#POST /rest/dependency-map/1.0/diagram
#POST /rest/dependency-map/1.0/linkConfig
#GET /plugins/servlet/dependency-map/diagram
#POST /rest/webResources/1.0/resources
#GET /rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50
#POST /rest/webResources/1.0/resources

class TestChangeDiagram:
    @max_freq(50/3600)
    @print_timing
    def test_change_diagram_config(self, base_url, session):
        HOSTNAME = os.environ.get('application_hostname')
        # Get user
        diagrams_response = session.get('/rest/dependency-map/1.0/user')
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]
        print_in_shell("User key: " + userKey)

        # Create diagram
        payload ={
          'name':"D100",
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
        print_in_shell('payload=', payload)
        diagrams_response = session.post('/rest/dependency-map/1.0/diagram',
            json=payload)
        print('diag resp=',str(diagrams_response.text))
        assert diagrams_response.status_code == 200
        newDiagram = diagrams_response.json()
        diagramId = str(newDiagram["id"])
        print_in_shell('diagramid=' +diagramId)

        saveRemoveDiagramCmd(diagramId)

        # Get all priorities
        diagrams_response = session.get('/rest/dependency-map/1.0/fieldOption/priority')
        assert diagrams_response.status_code == 200
        priorityItem = diagrams_response.json()[4]
        priorityItemId = str(priorityItem['id'])
        print_in_shell('priorityItemId=' + priorityItemId)

        #Get colore palete entry for diagram for field=priority option=5
        diagrams_response = session.get('/rest/dependency-map/1.0/boxColor/' + diagramId)
        assert diagrams_response.status_code == 200
        value = diagrams_response.text
        if not value:
           print_in_shell( "No response value")
        else:
           print_in_shell( diagrams_response.json() )

        #create box coloure resource entry
        payload = {"diagramId":diagramId,"fieldKey":"priority","fieldOptionId":priorityItemId,"colorPaletteEntryId":4}
        diagrams_response = session.post('/rest/dependency-map/1.0/boxColor',
            json=payload)
        assert diagrams_response.status_code == 200
        print_in_shell( diagrams_response.json() )
