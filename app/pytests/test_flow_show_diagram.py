import requests
import pytest
import time
from fixtures import session
from fixtures import base_url
import os
import random
from maxfreq import max_freq
from conftest import print_in_shell
from conftest import print_timing_with_additional_arg
from conftest import getRandomProjectId
from conftest import getRandomFilter
from conftest import saveRemoveDiagramCmd


@pytest.fixture(scope="class")
def create_data(session):
    # Get user
    diagrams_response = session.get('/rest/dependency-map/1.0/user')
    assert diagrams_response.status_code == 200
    userKey = diagrams_response.json()["key"]
    print_in_shell("User key: " + userKey)


    ##################################################################################################
    #Create Diagram
    #################################################################################################
    # Get filter key
    diagrams_response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
    assert diagrams_response.status_code == 200

    #Get filterKey randomly among the project in the project file
    filterKey= getRandomFilter(session)

    field= 'status'
    field2='priority'


    # Create diagram
    payload ={
      'name':"F100",
      'author':userKey,
      'lastEditedBy':userKey,
      'layoutId':2,
      'filterKey': filterKey,
      'boxColorFieldKey': field,
      'groupedLayoutFieldKey': field,
      'matrixLayoutHorizontalFieldKey': field,
      'matrixLayoutVerticalFieldKey': field2,
      'showTypeIcons': True,
      'parallelIssueBatches': 4,
      'issuesPerRow': 5,
      'secondaryIssues': 1,
      'boxType': 0
    }

    diagrams_response = session.post('/rest/dependency-map/1.0/diagram',
        json=payload)
    assert diagrams_response.status_code == 200
    diagramId = str(diagrams_response.json()['id'])
    print_in_shell("Nytt diagram med id="  + diagramId )
    saveRemoveDiagramCmd(diagramId)


    #update box colore resource entry, created if not exists.
    payload = {"diagramId":diagramId,"fieldKey":"status","fieldOptionId":1,"colorPaletteEntryId":5}
    diagrams_response = session.post('/rest/dependency-map/1.0/boxColor',
        json=payload)
    assert diagrams_response.status_code == 200
    #print_in_shell( diagrams_response.json() )

    #######################################################
    # Creae linkConfig
    #######################################################

    #JIRA Get list of available link types
    diagrams_response = session.get('/rest/api/2/issueLinkType')
    issueLinkTypeId = diagrams_response.json()['issueLinkTypes'][0]['id']
    print_in_shell("issueLinkTypeId=" + issueLinkTypeId)

    # Create linkConfig
    payload = {
        'diagramId': int(diagramId),
        'linkKey': int(issueLinkTypeId),
        'visible': True,
        'dashType': 0,
        'width': 0,
        'colorPaletteEntryId': 20
    }
    print_in_shell('payload', payload)

    diagrams_response = session.post('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId,
        json=payload)
    assert diagrams_response.status_code == 200, diagrams_response.text
    newLinkConfig = diagrams_response.json()
    print_in_shell('newLinkConfig', newLinkConfig)
    #linkConfigId = str(newLinkConfig["id"])
    #print_in_shell("linkConfigId=" + linkConfigId)

    # yield diagramId
    #
    # diagrams_response2 = session.delete('/rest/dependency-map/1.0/diagram/' + diagramId)
    # assert diagrams_response2.status_code == 200
    # print_in_shell("Deleted diagram id=" + diagramId)

    return diagramId


class TestFlowShowDiagram:
    @max_freq(1000/3600)
#    @print_timing_with_additional_arg

    def test_show_diagram_flow_sd(self, base_url, session, create_data):
        print_in_shell('test_show_diagram_flow_sd start')
        diagramId=create_data
        print_in_shell('diagramId', diagramId)
        #Get all diagrams
        HOSTNAME = os.environ.get('application_hostname')
        diagrams_response = session.get('/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200, diagrams_response.text

        resp = session.get('/rest/api/latest/project')
        assert resp.status_code == 200
        #result = resp.json()
        #length = len(result)
        project_id=getRandomProjectId()
        print_in_shell('project_id', project_id)

        issue_ids = []
        startAt = 0
        while True:
            resp = session.get(f'/rest/api/latest/search?maxResults=50&startAt={startAt}&jql=project={project_id}&fields=key')
            assert resp.status_code == 200
            result = resp.json()
            if startAt >= result['total'] or startAt > 500 or not('issues' in result):
                break
            issue_ids.extend(list(map(lambda issue : issue['id'], result['issues'])))
            startAt = len(issue_ids)
        print_in_shell(issue_ids)

        #Get color palet entries
        diagrams_response = session.get('/rest/dependency-map/1.0/colorPaletteEntry?paletteId=' + '0')
        assert diagrams_response.status_code == 200
        colorPaletteEntryId =  diagrams_response.json() [-1]["id"]
        print_in_shell("colorPaletteEntryId=" + str(colorPaletteEntryId))

        #Get color palet entries
        diagrams_response = session.get('/rest/dependency-map/1.0/colorPaletteEntry?paletteId=' + '1')
        assert diagrams_response.status_code == 200
        colorPaletteEntryId =  diagrams_response.json() [-1]["id"]
        print_in_shell("colorPaletteEntryId=" + str(colorPaletteEntryId))

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('/rest/dependency-map/1.0/boxColor/' + diagramId)
        assert diagrams_response.status_code == 200, diagrams_response.text
        value = diagrams_response.text
        if not value:
            print_in_shell( "No response value fieldId 1")
        else:
            print_in_shell( diagrams_response.text )

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('/rest/dependency-map/1.0/boxColor/' + diagramId)
        assert diagrams_response.status_code == 200
        value = diagrams_response.text
    #    if not value:
    #        print_in_shell( "No response value fieldId 2")
    #    else:
    #       print_in_shell( diagrams_response.json() )

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('/rest/dependency-map/1.0/boxColor/' + diagramId)
        assert diagrams_response.status_code == 200
        value = diagrams_response.text
    #    if not value:
    #        print_in_shell( "No response value fieldId 3")
    #    else:
    #        print_in_shell( diagrams_response.json() )

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('/rest/dependency-map/1.0/boxColor/' + diagramId)
        assert diagrams_response.status_code == 200
        value = diagrams_response.text
    #    if not value:
    #        print_in_shell( "No response value fieldId 4")
    #    else:
    #        print_in_shell( diagrams_response.json() )

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('/rest/dependency-map/1.0/boxColor/' + diagramId)
        assert diagrams_response.status_code == 200
        value = diagrams_response.text
    #    if not value:
    #        print_in_shell( "No response value fieldId 5")
    #    else:
    #        print_in_shell( diagrams_response.json() )

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('/rest/dependency-map/1.0/boxColor/' + diagramId)
        assert diagrams_response.status_code == 200
        value = diagrams_response.text
    #    if not value:
    #        print_in_shell( "No response value fieldId -1")
    #    else:
    #        print_in_shell( diagrams_response.json() )

        #JIRA Get list of available fileds
        diagrams_response = session.get('/rest/api/2/field')
        assert diagrams_response.status_code == 200
    #    value = diagrams_response.json()[0]
    #    content = diagrams_response.text
    #    if not value:
    #        print_in_shell( "No response value field")
    #    else:
    #        print_in_shell(value)

        #JIRA Get list of available link types
        diagrams_response = session.get('/rest/api/2/issueLinkType')
        assert diagrams_response.status_code == 200
        issueLinkTypeId = diagrams_response.json()['issueLinkTypes'][0]['id']
    #    print_in_shell("issueLinkTypeId=" + issueLinkTypeId)

        #Get all link configs
        diagrams_response = session.get('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId)
    #    print_in_shell( diagrams_response.json())
