import requests
from conftest import print_timing_with_additional_arg
from fixtures import session
from fixtures import base_url
import pytest
from generatetests import pytest_generate_tests
import os
import re
from os import path
import random
from maxfreq import max_freq
from conftest import print_in_shell
from conftest import getRandomProjectId
from conftest import saveRemoveIssueLinkCmd
from conftest import getFilterId

#POST /rest/api/2/issueLink
#GET /rest/api/2/issue/10000

_project_id = 0

basepath = path.dirname(__file__)
out_file_path = path.abspath(path.join(basepath, "deleteCreatedObjects"))


@pytest.fixture(scope="class")
def create_data(session):
   # print_in_shell("Create diagram")
   # session = requests.session()

   # Get user
   diagrams_response = session.get('/rest/dependency-map/1.0/user')
   assert diagrams_response.status_code == 200
   userKey = diagrams_response.json()["key"]
   print_in_shell("User key: " + userKey)

   # Get filter key
   diagrams_response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
   assert diagrams_response.status_code == 200

   # Get field priority
   diagrams_response = session.get('/rest/dependency-map/1.0/field/priority')
   assert diagrams_response.status_code == 200
   field = diagrams_response.json()["id"]

   # Get field fixVersions
   diagrams_response = session.get('/rest/dependency-map/1.0/field/fixVersions')
   assert diagrams_response.status_code == 200
   field2= diagrams_response.json()["id"]

   # Get project and filter  id from the list of projects we shall use, saved in a file
   projectId=getRandomProjectId()
   filterId = getFilterId(projectId)

   # Create diagram nedan går att skapa men inte att öppna
   #payload ={ 'name':"G100", 'author': userKey,
   #           'lastEditedBy':userKey, 'layoutId':0, 'filterKey': filterId,
   #           'boxColorFieldKey': field, 'groupedLayoutFieldKey': field,
   #           'matrixLayoutHorizontalFieldKey': field2, 'matrixLayoutVerticalFieldKey': field2}

   # Create diagram
   payload ={ 'name':"G100", 'author': userKey,
              'lastEditedBy':userKey, 'layoutId':0, 'filterKey': filterId,
              'boxColorFieldKey': field, 'groupedLayoutFieldKey': field2,
              'matrixLayoutHorizontalFieldKey': 'status', 'matrixLayoutVerticalFieldKey': field2}

   diagrams_response = session.post('/rest/dependency-map/1.0/diagram',
                                    json=payload)
   assert diagrams_response.status_code == 200
   diagramId = diagrams_response.json()['id']
   diagramIdStr = str(diagramId)


   #create box colore resource entries.
   payload = {"diagramId":diagramId,"fieldId":"status","fieldOptionId":1,"colorPaletteEntryId":5}
   diagrams_response = session.post('/rest/dependency-map/1.0/boxColor',
                                    json=payload)
   assert diagrams_response.status_code == 200

   payload = {"diagramId":diagramId,"fieldId":"status","fieldOptionId":2,"colorPaletteEntryId":6}
   diagrams_response = session.post('/rest/dependency-map/1.0/boxColor',
                                    json=payload)
   assert diagrams_response.status_code == 200

   payload = {"diagramId":diagramId,"fieldId":"status","fieldOptionId":3,"colorPaletteEntryId":7}
   diagrams_response = session.post('/rest/dependency-map/1.0/boxColor',
                                    json=payload)
   assert diagrams_response.status_code == 200

   payload = {"diagramId":diagramId,"fieldId":"status","fieldOptionId":4,"colorPaletteEntryId":8}
   diagrams_response = session.post('/rest/dependency-map/1.0/boxColor',
                                    json=payload)
   assert diagrams_response.status_code == 200


   #Create link config entries
   # Create linkConfig

   #Get color palet entrie
   diagrams_response = session.get('/rest/dependency-map/1.0/colorPaletteEntry?paletteId=' + '1')
   assert diagrams_response.status_code == 200
   print(diagrams_response.json())

   colorPaletteEntryId = diagrams_response.json()[14]["id"]
   colorPaletteEntryId2 = diagrams_response.json()[10]["id"]
   colorPaletteEntryId3 = diagrams_response.json()[12]["id"]

   diagrams_response = session.get('/rest/api/2/issueLinkType')
   issueLinkTypeIdStr = diagrams_response.json()['issueLinkTypes'][0]['id']
   issueLinkTypeId= int(issueLinkTypeIdStr)
   issueLinkTypeId2Str = diagrams_response.json()['issueLinkTypes'][1]['id']
   issueLinkTypeId2= int(issueLinkTypeId2Str)
   issueLinkTypeId3Str = diagrams_response.json()['issueLinkTypes'][2]['id']
   issueLinkTypeId3= int(issueLinkTypeId3Str)
   payload = { 'diagramId': diagramId, 'linkKey': issueLinkTypeId, 'visible': True , 'dashType': 0, 'width': 0, 'colorPaletteEntryId': colorPaletteEntryId}

   diagrams_response = session.post('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramIdStr,
                                    json=payload)
   assert(diagrams_response.status_code == 200)

   payload = { 'diagramId': diagramId, 'linkKey': issueLinkTypeId2, 'visible': True , 'dashType': 0, 'width': 0, 'colorPaletteEntryId': colorPaletteEntryId2}
   diagrams_response = session.post('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramIdStr,
                                    json=payload)
   assert(diagrams_response.status_code == 200)

   payload = { 'diagramId': diagramId, 'linkKey': issueLinkTypeId3, 'visible': True , 'dashType': 0, 'width': 0, 'colorPaletteEntryId': colorPaletteEntryId3}
   diagrams_response = session.post('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramIdStr,
                                    json=payload)
   assert(diagrams_response.status_code == 200)

   yield {'diagramId': diagramIdStr,  'projectId':projectId, 'filterId': filterId}
   diagrams_response2 = session.delete('/rest/dependency-map/1.0/diagram/' + diagramIdStr)
   assert diagrams_response2.status_code == 200
   print_in_shell("Deleted diagram id=" + diagramIdStr)

   return {'diagramId': diagramIdStr,  'projectId':projectId, 'filerId': filterId}

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


class TestCreateLink:
    @max_freq(500/3600)
    @print_timing_with_additional_arg
    def test_show_diagram_flow_ci(self, base_url, session, create_data):
        print(create_data)
        diagramIdStr = create_data['diagramId']
        projectId = create_data['projectId']
        filterIdStr= create_data['filterId']
        print(filterIdStr)

        # To make it thread save need to create the diagram before removing
        # Get user
        diagrams_response = session.get('/rest/dependency-map/1.0/user')
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]

        # Get filter key
        diagrams_response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
        assert diagrams_response.status_code == 200

        #Get favoritDiagram
        diagrams_response = session.get('/rest/dependency-map/1.0/favoriteDiagram')
        assert diagrams_response.status_code == 200
        #Get diagrams with filterKey
        diagrams_response = session.get('/rest/dependency-map/1.0/diagram?filterKey=' + filterIdStr + '&searchTerm=&sortBy=name&reverseSort=&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200

        #   #Get filter
        diagrams_response = session.get('/rest/api/2/filter/' + filterIdStr)
        assert diagrams_response.status_code == 200

        ############# When opening diagram
        #Get diagram
        diagrams_response = session.get('/rest/dependency-map/1.0/diagram/' + diagramIdStr)
        assert diagrams_response.status_code == 200

        #Get color palet entrie
        diagrams_response = session.get('/rest/dependency-map/1.0/colorPaletteEntry?palettId=' + '0')
        assert diagrams_response.status_code == 200

        #Get color palet entrie
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

        # Get field priority
        diagrams_response = session.get('/rest/dependency-map/1.0/field/status')
        assert diagrams_response.status_code == 200

        # Get field options - status
        diagrams_response = session.get('/rest/dependency-map/1.0/fieldOption/status')
        assert diagrams_response.status_code == 200

        # Get field options - fixVersions
        diagrams_response = session.get('/rest/dependency-map/1.0/fieldOption/fixVersions')
        assert diagrams_response.status_code == 200

        # Get issue linktype #
        diagrams_response = session.get('/rest/api/2/issueLinkType')
        assert diagrams_response.status_code == 200

        # Get filter moved to the next section
        #diagrams_response = session.get('/rest/dependency-map/1.0/filter' + filterIdStr)
        #assert diagrams_response.status_code == 200
        #searchUrl = diagrams_response.json()['searchUrl']
        ##remove everytning before '/rest/api/2/search'
        #shortSearchUrl = re.sub("/rest/api/2/search?", '', searchUrl)

        #diagrams_response = session.get(shortSearchUrl + "&fields=priority,status,fixVersions,assignee,duedate,summary,issuelinks&startAt=0&maxResults=50")
        #assert diagrams_response.status_code == 200

        # Get field priority
        diagrams_response = session.get('/rest/dependency-map/1.0/field/status')
        assert diagrams_response.status_code == 200

        # Get field options - status
        diagrams_response = session.get('/rest/dependency-map/1.0/fieldOption/status')
        assert diagrams_response.status_code == 200

        # Get field options - fixVersions
        diagrams_response = session.get('/rest/dependency-map/1.0/fieldOption/fixVersions')
        assert diagrams_response.status_code == 200
        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('/rest/dependency-map/1.0/boxColor?diagramId=' + diagramIdStr + '&fieldId=priority')
        assert diagrams_response.status_code == 200
        value = diagrams_response.text

    @max_freq(500/3600)
    @print_timing_with_additional_arg
    def test_create_issue_link_flow_ci(self, base_url, session, create_data):
        projectId = create_data['projectId']
        filterIdStr= create_data['filterId']
      #  print_in_shell("projectId=" + projectId )

        #JIRA Get list of available issues
        # Get filter
        diagrams_response = session.get('/rest/api/2/filter/' + filterIdStr)
        assert diagrams_response.status_code == 200
        searchUrl = diagrams_response.json()['searchUrl']
        #remove everytning before '/rest/api/2/search'
        startPos = searchUrl.find("/rest/api/2/search?")
        endPos = len(searchUrl)
        shortSearchUrl = searchUrl[startPos:endPos]
        diagrams_response = session.get(shortSearchUrl + "&fields=priority,status,fixVersions,assignee,duedate,summary,issuelinks&startAt=0&maxResults=50")
        assert diagrams_response.status_code == 200

        if len(diagrams_response.json()['issues']) >= 3:
            assert diagrams_response.status_code == 200
            to_issue_id = diagrams_response.json()['issues'][0]['id']
            to_issue_Key = diagrams_response.json()['issues'][0]['key']
            from_issue_id = diagrams_response.json()['issues'][2]['id']
            from_issue_Key = diagrams_response.json()['issues'][2]['key']

            #JIRA Get list of available link types
            issueLinkTypeId = get_link_type(session)

            #before
            diagrams_response = session.get('/rest/api/2/issue/' + from_issue_id)
            before_issue_links = diagrams_response.json()['fields']['issuelinks']
            before_size = len(before_issue_links)

            #JIRA create link #
            payload = { 'type': { 'id': issueLinkTypeId},
                        'inwardIssue': { 'id': to_issue_id },
                        'outwardIssue': { 'id': from_issue_id}}
            diagrams_response = session.post('/rest/api/2/issueLink',
                                             json= payload)
            assert diagrams_response.status_code == 201
            #after#
            diagrams_response = session.get('/rest/api/2/issue/' + from_issue_id)
            issue_links = diagrams_response.json()['fields']['issuelinks']
            if (len(issue_links) > before_size):
                issueLinksId = 0
                for issueLink in issue_links:
                   if 'inwardIssue' in issueLink and  issueLink['inwardIssue']:
                       if  issueLink['inwardIssue']['id']==to_issue_id:
                           issueLinksId = issueLink['id']

                #issueLinksId = issueLinks[-1]['id']
                if issueLinksId!=0:
                   try:
                       saveRemoveIssueLinkCmd(issueLinksId)
                   except IOError:
                       print_in_shell("File not accessible")


