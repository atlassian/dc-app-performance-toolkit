import requests
from fixtures import session
import pytest
from generatetests import pytest_generate_tests
import os
import random

#POST /rest/api/2/issueLink
#GET /rest/api/2/issue/10000

_diagram_id = '0'
_project_id = 0


@pytest.fixture(scope="class")
def create_data(session):
    print("Create diagram")
    global _diagram_id
   # session = requests.session()
    HOSTNAME = os.environ.get('application_hostname')

    # Get user
    diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/user')
    assert diagrams_response.status_code == 200
    userKey = diagrams_response.json()["key"]
    print("User key: " + userKey)

    # Get filter key
    diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
    assert diagrams_response.status_code == 200
    filterKey= str(diagrams_response.json()["filters"][1]["filterKey"])

    # Get field status
    diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/field/status')
    assert diagrams_response.status_code == 200
    field= diagrams_response.json()["id"]

    # Create diagram
    payload ={ 'name':"G100", 'author': userKey,
               'lastEditedBy':userKey, 'layoutId':0, 'filterKey': filterKey,
               'boxColorFieldKey': field, 'groupedLayoutFieldKey': field,
               'matrixLayoutHorizontalFieldKey': 'fixVersions', 'matrixLayoutVerticalFieldKey': 'fixVersions'}

    diagrams_response = session.post('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram',
                                     json=payload)
    assert diagrams_response.status_code == 200
    diagramId = diagrams_response.json()['id']
    diagramKey = str(diagramId)
    _diagram_id= diagramKey

    #create box colore resource entries.
    payload = {"diagramId":diagramId,"fieldId":"priority","fieldOptionId":1,"colorPaletteEntryId":5}
    diagrams_response = session.post('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor',
                                     json=payload)
    assert diagrams_response.status_code == 200

    payload = {"diagramId":diagramId,"fieldId":"priority","fieldOptionId":2,"colorPaletteEntryId":6}
    diagrams_response = session.post('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor',
                                     json=payload)
    assert diagrams_response.status_code == 200

    payload = {"diagramId":diagramId,"fieldId":"priority","fieldOptionId":3,"colorPaletteEntryId":7}
    diagrams_response = session.post('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor',
                                     json=payload)
    assert diagrams_response.status_code == 200

    payload = {"diagramId":diagramId,"fieldId":"priority","fieldOptionId":4,"colorPaletteEntryId":8}
    diagrams_response = session.post('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor',
                                     json=payload)
    assert diagrams_response.status_code == 200

    #Create link config entries
    # Create linkConfig
    diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/api/2/issueLinkType')
    issueLinkTypeId = diagrams_response.json()['issueLinkTypes'][0]['id']

    issueLinkTypeId2 = diagrams_response.json()['issueLinkTypes'][1]['id']
    issueLinkTypeId3 = diagrams_response.json()['issueLinkTypes'][2]['id']

    payload = { 'diagramId': diagramKey, 'linkKey': issueLinkTypeId, 'visible': True, 'dashType': 0, 'width': 0, 'colorPaletteEntryId': 5}
    diagrams_response = session.post('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramKey,
                                     json=payload)
    assert(diagrams_response.status_code == 200)

    payload = { 'diagramId': diagramKey, 'linkKey': issueLinkTypeId2, 'visible': True, 'dashType': 0, 'width': 0, 'colorPaletteEntryId': 6}
    diagrams_response = session.post('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramKey,
                                     json=payload)
    assert(diagrams_response.status_code == 200)

    payload = { 'diagramId': diagramKey, 'linkKey': issueLinkTypeId3 , 'visible': True, 'dashType': 0, 'width': 0, 'colorPaletteEntryId': 1}
    diagrams_response = session.post('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramKey,
                                     json=payload)
    assert(diagrams_response.status_code == 200)

    yield _diagram_id  # provide the fixture value
    diagrams_response2 = session.delete('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram/' + _diagram_id)
    assert diagrams_response2.status_code == 200
    print("Deleted diagram id=" + _diagram_id)

def get_link_type(session):
    #JIRA Get list of available link types
    HOSTNAME = os.environ.get('application_hostname')
    issueLinkTypeId = 0
    diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/api/2/issueLinkType')
    issueLinkTypes = diagrams_response.json()['issueLinkTypes']
    for linkType in issueLinkTypes:
        print(linkType)
        if linkType["name"]=="Blocks":
            issueLinkTypeId=linkType["id"]
            break
    print(issueLinkTypeId)
    return issueLinkTypeId


class TestCreateLink:
    def test_show_diagram_flow_ci(self, session, create_data,):
        global _project_id
        print("INSIDE SHOW")
        HOSTNAME = os.environ.get('application_hostname')

        #Get diagram
        diagram_ids = []
        startAt = 0
        while True:
            resp =  session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50')
            assert resp.status_code == 200
            result=resp.json()
            if startAt >= result['total'] or startAt > 500:
                break
            diagram_ids.extend(list(map(lambda diagram : diagram['id'], result['values'])))
            startAt = len(diagram_ids)

        #Get project
        resp = session.get('http://' + HOSTNAME + ':8080/rest/api/latest/project')
        assert resp.status_code == 200
        result = resp.json()
        length = len(result)
        project_id=result[random.randint(0,length-1)]['id']
        _project_id = project_id

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
            print(startAt)
        print(issue_ids)



        #JIRA Get project with everything in it
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/api/2/search?jql=project+%3D+' + '10000' + '+ORDER+BY+Rank+ASC&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200
        #print(diagrams_response.json());

        # Get field priority
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/field/status')
        assert diagrams_response.status_code == 200

        # Get field fixVersion
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/field/fixVersions')
        assert diagrams_response.status_code == 200

        # Get field options - status
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/fieldOption/status')
        assert diagrams_response.status_code == 200

        # Get field options - fixVersions
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/fieldOption/fixVersions')
        assert diagrams_response.status_code == 200

        #Get color palet entries
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/colorPaletteEntry')
        assert diagrams_response.status_code == 200

        #Get color palet entrie
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/colorPaletteEntry?palettId=' + '3')
        assert diagrams_response.status_code == 200
        colorPaletteEntryId =  diagrams_response.json() [-1]["id"]
        #    print("colorPaletteEntryId=" + str(colorPaletteEntryId))

        #Get color palet entrie
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/colorPaletteEntry?palettId=' + '1')
        assert diagrams_response.status_code == 200

        #Get color palet entrie
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/colorPaletteEntry?palettId=' + '4')
        assert diagrams_response.status_code == 200

        #Get color palet entrie
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/colorPaletteEntry?palettId=' + '5')
        assert diagrams_response.status_code == 200

        #Get color palet entrie
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/colorPaletteEntry?palettId=' + '6')
        assert diagrams_response.status_code == 200

        #Get color palet entrie
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/colorPaletteEntry?palettId=' + '-1')
        assert diagrams_response.status_code == 200
        #Get color palet entrie
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/colorPaletteEntry?palettId=' + '10002')
        assert diagrams_response.status_code == 200
        #Get color palet entrie
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/colorPaletteEntry?palettId=' + '10000')
        assert diagrams_response.status_code == 200
        #Get color palet entrie
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/colorPaletteEntry?palettId=' + '10001')
        assert diagrams_response.status_code == 200
        #Get color palet entrie
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/colorPaletteEntry?palettId=' + '10003')
        assert diagrams_response.status_code == 200

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor?diagramId=' + _diagram_id + '&fieldId=priority&fieldOptionId=1')
        assert diagrams_response.status_code == 200
        value = diagrams_response.text

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor?diagramId=' + _diagram_id + '&fieldId=priority&fieldOptionId=2')
        assert diagrams_response.status_code == 200
        value = diagrams_response.text

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor?diagramId=' + _diagram_id + '&fieldId=priority&fieldOptionId=3')
        assert diagrams_response.status_code == 200
        value = diagrams_response.text

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor?diagramId=' + _diagram_id + '&fieldId=priority&fieldOptionId=4')
        assert diagrams_response.status_code == 200
        value = diagrams_response.text

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor?diagramId=' + _diagram_id + '&fieldId=priority&fieldOptionId=5')
        assert diagrams_response.status_code == 200
        value = diagrams_response.text

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor?diagramId=' + _diagram_id + '&fieldId=priority&fieldOptionId=-1')
        assert diagrams_response.status_code == 200
        value = diagrams_response.text

        #JIRA Get list of available fileds
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/api/2/field')
        assert diagrams_response.status_code == 200

        #JIRA Get list of available link types
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/api/2/issueLinkType')
        assert diagrams_response.status_code == 200
        issueLinkTypeId = diagrams_response.json()['issueLinkTypes'][0]['id']

        #Get all link configs
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/linkConfig?diagramId=' + _diagram_id)


    def test_create_issue_link_flow_ci(self, session, create_data):
        global _project_id
        print("INSIDE CREATE")
        HOSTNAME = os.environ.get('application_hostname')

        projectId = _project_id

        #JIRA Get list of available issues
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/api/2/search?jql=project=' + projectId)
        assert diagrams_response.status_code == 200
        issueId1 = diagrams_response.json()['issues'][0]['id']
        issueKey1 = diagrams_response.json()['issues'][0]['key']
        issueId2 = diagrams_response.json()['issues'][9]['id']

        #JIRA Get list of available link types
        issueLinkTypeId = get_link_type(session)

        ####
        #JIRA create link
        payload = { 'type': { 'id': issueLinkTypeId},
                    'inwardIssue': { 'id': issueId2 },
                    'outwardIssue': { 'id': issueId1}}
        diagrams_response = session.post('http://' + HOSTNAME + ':8080/rest/api/2/issueLink',
                                         json= payload)
        assert diagrams_response.status_code == 201
        print("issue created")

        ###
        #JIRA Get new issue links id
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/api/2/issue/' + issueKey1)
        issueLinks = diagrams_response.json()['fields']['issuelinks']
        issueLinksId = issueLinks[0]['id']
        print("New issue Links Id=" + issueLinksId);

