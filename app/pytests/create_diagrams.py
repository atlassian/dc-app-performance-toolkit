import requests
import json
from fixtures import session
from fixtures import base_url
from conftest import readProjectCmd
import os
from os import path
import random
import pathlib

HOSTNAME = os.environ.get('application_hostname')

basepath = path.dirname(__file__)
#CURRENT_PATH = pathlib.Path().absolute()
out_file_path = path.abspath(path.join(basepath, "deleteCreatedObjects"))

def getProjectIds(projectDict):
    result = []
    for project in projectDict:
        result.append(project['id'])
    return result

class TestCreateDiagram:

    def test_create_diagram(self, base_url, session):
        #Get filter key
        page = 0
        projectDict = readProjectCmd()
        projectIdList = getProjectIds(projectDict)
        filterKeyList =[]
        for  project in projectDict:
            filterKeyList.append(project["filterId"])
        print(str(filterKeyList))

        with open(out_file_path, "a") as f:
            # print( diagrams_response.json() );
            for filterKey in filterKeyList:
                print(filterKey)
                for c in range(0, 10):
                    diagramId = create_diagram(filterKey, session)
                    diagrams_delete_request = '/rest/dependency-map/1.0/diagram/' + diagramId
                    f.write(diagrams_delete_request)
                    f.write("\n")
        f.close()

def create_diagram(filterKey, session):
    # Get filter key
    HOSTNAME = os.environ.get('application_hostname')

    # Get field
    field = 'priority'
    print(field)

    # Get field
    field2 = 'status'
    print(field)

    # Get user
    diagrams_response = session.get('/rest/dependency-map/1.0/user')
    assert diagrams_response.status_code == 200
    userKey = diagrams_response.json()["key"]
    print("User key: " + userKey)

    # Create diagram
    payload = {
      'name': "A100",
      'author': userKey,
      'layoutId': 2,
      'filterId': filterKey,
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

    diagram_response = session.post('/rest/dependency-map/1.0/diagram',
                                    json=payload)
    assert diagram_response.status_code == 200
    diagramId = str(diagram_response.json()["id"])
    print("New diagram id: " + diagramId)

    # Create linkConfig
    payload = {
      'diagramId': diagramId,
      'linkKey': 10000,
      'visible': True,
      'dashType': 0,
      'width': 0,
      'colorPaletteEntryId': 20
    }

    diagrams_response = session.post('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId,
                                     json=payload)



    newLinkConfig = diagrams_response.json()
    linkConfigId = str(newLinkConfig["id"])
    print(linkConfigId)
    assert(diagrams_response.status_code == 200)

    change_color_mapping(session, diagramId)

    return diagramId

def change_color_mapping(session, diagramId):
    HOSTNAME = os.environ.get('application_hostname')

    # Get all priorities
    diagrams_response = session.get('/rest/dependency-map/1.0/fieldOption/status')
    assert diagrams_response.status_code == 200
    nrOfFieldOptions=len(diagrams_response.json())
    fieldIemList = diagrams_response.json()
    #Nr of field options
    print(nrOfFieldOptions)

    for field in fieldIemList:
        fieldOptionId = field["id"]
        colorPaletteEntryId = random.randint(0,19)
        #create box coloure resource entry
        payload = {
          "diagramId":diagramId,
          "fieldId":"status",
          "fieldOptionId":fieldOptionId,
          "colorPaletteEntryId": colorPaletteEntryId
        }
        diagrams_response = session.post('/rest/dependency-map/1.0/boxColor', json=payload)
        assert diagrams_response.status_code == 200
        print( diagrams_response.json() )
        #boxColorResource = diagrams_response.json()['id']
