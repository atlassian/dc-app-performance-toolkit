import requests
import pytest
import time
from fixtures import session
import os
import random
from maxfreq import max_freq
from conftest import print_in_shell

#GET /rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50 HTTP/1.1" 200 1040 3 "http://localhost:8080/plugins/servlet/dependency-map/diagram?r
#GET /rest/api/2/search?jql=project+%3D+SCRUM+ORDER+BY+Rank+ASC&startAt=0&maxResults=50 HTTP/1.1" 200 7802 44 "http://localhost:8080/plugins/servlet/dependenc
#GET /rest/dependency-map/1.0/field/priority HTTP/1.1" 200 87 1 "http://localhost:8080/plugins/servlet/dependency-map/diagram?renderDiagramId=114" "Mozilla/5.
#GET /rest/dependency-map/1.0/field/fixVersions HTTP/1.1" 200 79 1 "http://localhost:8080/plugins/servlet/dependency-map/diagram?renderDiagramId=114" "Mozilla
#GET /rest/dependency-map/1.0/fieldOption/priority HTTP/1.1" 200 124 1 "http://localhost:8080/plugins/servlet/dependency-map/diagram?renderDiagramId=114" "Moz
#GET /rest/dependency-map/1.0/fieldOption/fixVersions HTTP/1.1" 200 124 1 "http://localhost:8080/plugins/servlet/dependency-map/diagram?renderDiagramId=114" "
#GET /rest/dependency-map/1.0/colorPaletteEntry?paletteId=0 HTTP/1.1" 200 287 2 "http://localhost:8080/plugins/servlet/dependency-map/diagram?renderDiagramId=
#GET /rest/dependency-map/1.0/colorPaletteEntry?paletteId=1 HTTP/1.1" 200 295 1 "http://localhost:8080/plugins/servlet/dependency-map/diagram?renderDiagramId=
#GET /rest/dependency-map/1.0/boxColor?diagramId=114&fieldId=priority&fieldOptionId=1 HTTP/1.1" 200 40 2 "http://localhost:8080/plugins/servlet/dependency-map
#GET /rest/dependency-map/1.0/boxColor?diagramId=114&fieldId=priority&fieldOptionId=2 HTTP/1.1" 200 40 2 "http://localhost:8080/plugins/servlet/dependency-map
#GET /rest/dependency-map/1.0/boxColor?diagramId=114&fieldId=priority&fieldOptionId=3 HTTP/1.1" 200 40 1 "http://localhost:8080/plugins/servlet/dependency-map
#GET /rest/dependency-map/1.0/boxColor?diagramId=114&fieldId=priority&fieldOptionId=4 HTTP/1.1" 200 40 1 "http://localhost:8080/plugins/servlet/dependency-map
#GET /rest/dependency-map/1.0/boxColor?diagramId=114&fieldId=priority&fieldOptionId=5 HTTP/1.1" 200 40 3 "http://localhost:8080/plugins/servlet/dependency-map
#GET /rest/dependency-map/1.0/boxColor?diagramId=114&fieldId=priority&fieldOptionId=-1 HTTP/1.1" 200 40 2 "http://localhost:8080/plugins/servlet/dependency-ma
#GET /rest/api/2/field HTTP/1.1" 200 1417 2 "http://localhost:8080/plugins/servlet/dependency-map/diagram?renderDiagramId=114" "Mozilla/5.0 (Windows NT 10.0;
#GET /rest/api/2/issueLinkType HTTP/1.1" 200 229 2 "http://localhost:8080/plugins/servlet/dependency-map/diagram?renderDiagramId=114" "Mozilla/5.0 (Windows NT
#GET /rest/dependency-map/1.0/linkConfig?diagramId=114 HTTP/1.1" 200 44 2 "http://localhost:8080/plugins/servlet/dependency-map/diagram?renderDiagramId=114" "


@pytest.fixture(scope="class")
def create_data(session):
    HOSTNAME = os.environ.get('application_hostname')
    # Get user
    diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/user')
    assert diagrams_response.status_code == 200
    userKey = diagrams_response.json()["key"]
    print_in_shell("User key: " + userKey)


    ##################################################################################################
    #Create Diagram
    #################################################################################################
    # Get filter key
    diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
    assert diagrams_response.status_code == 200
    filterKey= str(diagrams_response.json()["filters"][1]["filterKey"])

    # Get field status
    diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/field/status')
    assert diagrams_response.status_code == 200
    field= diagrams_response.json()["id"]

    # Get field sprint
    diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/field/sprint')
    assert diagrams_response.status_code == 200
    field2= diagrams_response.json()["id"]


    # Create diagram
    payload ={ 'name':"D100", 'author':userKey,
       'lastEditedBy':userKey, 'layoutId':2, 'filterKey': filterKey,
        'boxColorFieldKey': field, 'groupedLayoutFieldKey': field,
        'matrixLayoutHorizontalFieldKey': field, 'matrixLayoutVerticalFieldKey': field2}

    diagrams_response = session.post('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram',
        json=payload)
    assert diagrams_response.status_code == 200
    diagramId = str(diagrams_response.json()['id'])
    print_in_shell("Nytt diagram med id="  + diagramId )


    #update box colore resource entry, created if not exists.
    payload = {"diagramId":diagramId,"fieldId":"status","fieldOptionId":1,"colorPaletteEntryId":5}
    diagrams_response = session.post('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor',
        json=payload)
    assert diagrams_response.status_code == 200
    #print_in_shell( diagrams_response.json() )

    #######################################################
    # Creae linkConfig
    #######################################################

    #JIRA Get list of available link types
    diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/api/2/issueLinkType')
    issueLinkTypeId = diagrams_response.json()['issueLinkTypes'][0]['id']
    print_in_shell("issueLinkTypeId=" + issueLinkTypeId)

    # Create linkConfig
    payload = { 'diagramId': diagramId, 'linkKey': issueLinkTypeId, 'visible': True, 'dashType': 0, 'width': 0, 'colorPaletteEntryId': 5}

    diagrams_response = session.post('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId,
        json=payload)
    assert(diagrams_response.status_code == 200)
    newLinkConfig = diagrams_response.json()
    linkConfigId = str(newLinkConfig["id"])
    print_in_shell("linkConfigId=" + linkConfigId)

    yield diagramId

    diagrams_response2 = session.delete('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram/' + diagramId)
    assert diagrams_response2.status_code == 200
    print_in_shell("Deleted diagram id=" + diagramId)

    return diagramId


class TestFlowShowDiagram:
    @max_freq(1000/3600)
    def test_show_diagram_flow_sd(self, create_data, session):
        diagramId=create_data
        #Get all diagrams
        HOSTNAME = os.environ.get('application_hostname')
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200

        resp = session.get('http://' + HOSTNAME + ':8080/rest/api/latest/project')
        assert resp.status_code == 200
        result = resp.json()
        length = len(result)
        project_id=result[random.randint(0,length-1)]['id']

        issue_ids = []
        startAt = 0
        while True:
            resp = session.get('http://' + HOSTNAME + f':8080/rest/api/latest/search?maxResults=50&startAt={startAt}&jql=project={project_id}&fields=key')
            assert resp.status_code == 200
            result = resp.json()
            if startAt >= result['total'] or startAt > 500:
                break
            issue_ids.extend(list(map(lambda issue : issue['id'], result['issues'])))
            startAt = len(issue_ids)
        print_in_shell(issue_ids)

        # Get field priority
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/field/priority')
        assert diagrams_response.status_code == 200

        # Get field fixVersion
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/field/fixVersions')
        assert diagrams_response.status_code == 200

        #Get color palet entries
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/colorPaletteEntry?palettId=' + '0')
        assert diagrams_response.status_code == 200
        colorPaletteEntryId =  diagrams_response.json() [-1]["id"]
    #    print_in_shell("colorPaletteEntryId=" + str(colorPaletteEntryId))

        #Get color palet entries
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/colorPaletteEntry?palettId=' + '1')
        assert diagrams_response.status_code == 200
        colorPaletteEntryId =  diagrams_response.json() [-1]["id"]
    #    print_in_shell("colorPaletteEntryId=" + str(colorPaletteEntryId))

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor?diagramId=' + diagramId + '&fieldId=priority&fieldOptionId=1')
        assert diagrams_response.status_code == 200
        value = diagrams_response.text
    #    if not value:
    #        print_in_shell( "No response value fieldId 1")
    #    else:
    #        print_in_shell( diagrams_response.json() )

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor?diagramId=' + diagramId + '&fieldId=priority&fieldOptionId=2')
        assert diagrams_response.status_code == 200
        value = diagrams_response.text
    #    if not value:
    #        print_in_shell( "No response value fieldId 2")
    #    else:
    #       print_in_shell( diagrams_response.json() )

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor?diagramId=' + diagramId + '&fieldId=priority&fieldOptionId=3')
        assert diagrams_response.status_code == 200
        value = diagrams_response.text
    #    if not value:
    #        print_in_shell( "No response value fieldId 3")
    #    else:
    #        print_in_shell( diagrams_response.json() )

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor?diagramId=' + diagramId + '&fieldId=priority&fieldOptionId=4')
        assert diagrams_response.status_code == 200
        value = diagrams_response.text
    #    if not value:
    #        print_in_shell( "No response value fieldId 4")
    #    else:
    #        print_in_shell( diagrams_response.json() )

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor?diagramId=' + diagramId + '&fieldId=priority&fieldOptionId=5')
        assert diagrams_response.status_code == 200
        value = diagrams_response.text
    #    if not value:
    #        print_in_shell( "No response value fieldId 5")
    #    else:
    #        print_in_shell( diagrams_response.json() )

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor?diagramId=' + diagramId + '&fieldId=priority&fieldOptionId=-1')
        assert diagrams_response.status_code == 200
        value = diagrams_response.text
    #    if not value:
    #        print_in_shell( "No response value fieldId -1")
    #    else:
    #        print_in_shell( diagrams_response.json() )

        #JIRA Get list of available fileds
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/api/2/field')
        assert diagrams_response.status_code == 200
    #    value = diagrams_response.json()[0]
    #    content = diagrams_response.text
    #    if not value:
    #        print_in_shell( "No response value field")
    #    else:
    #        print_in_shell(value)

        #JIRA Get list of available link types
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/api/2/issueLinkType')
        assert diagrams_response.status_code == 200
        issueLinkTypeId = diagrams_response.json()['issueLinkTypes'][0]['id']
    #    print_in_shell("issueLinkTypeId=" + issueLinkTypeId)

        #Get all link configs
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId)
    #    print_in_shell( diagrams_response.json())









             