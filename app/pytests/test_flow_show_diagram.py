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
from conftest import getFilterId
from conftest import saveRemoveDiagramCmd

@pytest.fixture(scope="class")
def create_data(session):
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
    field= diagrams_response.json()["id"]

    # Get field status
    diagrams_response = session.get('/rest/dependency-map/1.0/field/status')
    assert diagrams_response.status_code == 200
    field2 = diagrams_response.json()["id"]

    # Get field fix version
    diagrams_response = session.get('/rest/dependency-map/1.0/field/fixVersions')
    assert diagrams_response.status_code == 200
    field3 = diagrams_response.json()["id"]

    # Get project and filter  id from the list of projects we shall use, saved in a file
    projectId=getRandomProjectId()
    filterId= getFilterId(projectId)

    # Create diagram
    payload = {'name': "F100", 'author': userKey,
               'lastEditedBy': userKey, 'layoutId': 2, 'filterKey': filterId,
               'boxColorFieldKey': field, 'groupedLayoutFieldKey': field2,
               'matrixLayoutHorizontalFieldKey': field2, 'matrixLayoutVerticalFieldKey': field3}

    diagrams_response = session.post('/rest/dependency-map/1.0/diagram',
        json=payload)
    assert diagrams_response.status_code == 200
    diagramId = diagrams_response.json()['id']
    diagramIdStr = str(diagramId)
    print_in_shell("Nytt diagram med id="  + diagramIdStr )
    saveRemoveDiagramCmd(diagramIdStr)

    ##############################################################
    # Add to favorit
    ##############################################################

    #Get favoritDiagram
    diagrams_response = session.get('/rest/dependency-map/1.0/favoriteDiagram')
    assert diagrams_response.status_code == 200
    favoritDiagrams = diagrams_response.json()

    #add to favorits
    favoritDiagrams.insert(0,diagramId)
    payload = favoritDiagrams
    diagrams_response = session.post('/rest/dependency-map/1.0/favoriteDiagram')



    #Get favoritDiagram
    diagrams_response = session.get('/rest/dependency-map/1.0/favoriteDiagram')
    assert diagrams_response.status_code == 200
    favoritDiagrams = diagrams_response.json()


    #update box colore resource entry, created if not exists.
    payload = {"diagramId":diagramId,"fieldId":"status","fieldOptionId":1,"colorPaletteEntryId":5}
    diagrams_response = session.post('/rest/dependency-map/1.0/boxColor',
        json=payload)
    assert diagrams_response.status_code == 200
    #print_in_shell( diagrams_response.json() )
    #######################################################
    # Creae linkConfig
    #######################################################
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

    yield {'diagramId': diagramId,  'projectId':projectId, 'filterId': filterId}
    diagrams_response2 = session.delete('/rest/dependency-map/1.0/diagram/' + diagramIdStr)
    assert diagrams_response2.status_code == 200
    print_in_shell("Deleted diagram id=" + diagramIdStr)

    return {'diagramId': diagramId,  'projectId':projectId, 'filerId': filterId}


class TestFlowShowDiagram:
    @max_freq(1000/3600)
    @print_timing_with_additional_arg
    def test_show_diagram_flow_sd(self, base_url, session, create_data):
        filterIdStr= create_data['filterId']
        diagramId= create_data['diagramId']
        diagramIdStr= str(diagramId)
        # Get user
        diagrams_response = session.get('/rest/dependency-map/1.0/user')
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]
        print_in_shell("User key: " + userKey)
        #Get favoritDiagram
        diagrams_response = session.get('/rest/dependency-map/1.0/favoriteDiagram')
        assert diagrams_response.status_code == 200
        favoritDiagrams = diagrams_response.json()
        print(favoritDiagrams)
       # firstDiagId = favoritDiagrams[0]["diagramId"]

        for diag in favoritDiagrams:
            id =diag["diagramId"]

            diagrams_response = session.get('/rest/dependency-map/1.0/diagram/' + str(id))
            print(diagrams_response.json())
            filterKey = diagrams_response.json()['filterKey']
            assert diagrams_response.status_code == 200

            # Get filter key
            diagrams_response = session.get("/rest/api/2/filter/" + str(filterKey))
            assert diagrams_response.status_code == 200

        print(diagramIdStr)
        #Selecting and opening diagram
        diagrams_response = session.get('/rest/dependency-map/1.0/diagram/' + diagramIdStr)
        assert diagrams_response.status_code == 200

        #Get color palet entrie
        diagrams_response = session.get('/rest/dependency-map/1.0/colorPaletteEntry?paletteId=' + '0')
        assert diagrams_response.status_code == 200

        #Get color palet entrie
        diagrams_response = session.get('/rest/dependency-map/1.0/colorPaletteEntry?paletteId=' + '1')
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

        # Get linkConfig #
        diagrams_response = session.get('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramIdStr)
        assert diagrams_response.status_code == 200

        # Get field priority
        diagrams_response = session.get('/rest/dependency-map/1.0/field/priority')
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

        # Get field priority
        diagrams_response = session.get('/rest/dependency-map/1.0/field/status')
        assert diagrams_response.status_code == 200

        diagrams_response = session.get("/rest/api/2/filter/" + filterIdStr)
        assert diagrams_response.status_code == 200

        # Get field options - priority
        diagrams_response = session.get('/rest/dependency-map/1.0/fieldOption/priority')
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









             