import requests
import json
from fixtures import session
from fixtures import base_url
from conftest import readProjectCmd
import os
from os import path
import random
import pathlib

#GET /rest/api/2/issueLinkType HTTP/1.1" 200 229 3 "http://localhost:8080/plugins/servlet/dependency-map/diagram" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) A
#GET /rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25&_=1580893219884 HTTP/1.1" 200 153 2 "http://localhost:8080/plugins/servlet/dependenc
#GET /rest/dependency-map/1.0/field?searchTerm=&page=0&resultsPerPage=25&_=1580893250444 HTTP/1.1" 200 243 1 "http://localhost:8080/plugins/servlet/dependency
#GET /rest/dependency-map/1.0/field?searchTerm=&page=0&resultsPerPage=25&_=1580893254366 HTTP/1.1" 200 243 1 "http://localhost:8080/plugins/servlet/dependency
#GET /rest/dependency-map/1.0/user HTTP/1.1" 200 96 1 "http://localhost:8080/plugins/servlet/dependency-map/diagram" "Mozilla/5.0 (Windows NT 10.0; Win64; x64
#POST /rest/dependency-map/1.0/diagram HTTP/1.1" 200 226 2 "http://localhost:8080/plugins/servlet/dependency-map/diagram" "Mozilla/5.0 (Windows NT 10.0; Win64
#POST /rest/dependency-map/1.0/linkConfig HTTP/1.1" 200 134 5 "http://localhost:8080/plugins/servlet/dependency-map/diagram" "Mozilla/5.0 (Windows NT 10.0; Wi

# ??? POST /rest/webResources/1.0/resources HTTP/1.1" 200 494 3 "http://localhost:8080/plugins/servlet/dependency-map/diagram" "Mozilla/5.0 (Windows NT 10.0; Win64

#GET /rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50 HTTP/1.1" 200 960 3 "http://localhost:8080/plugins/servlet/dependency-map/diagram" "
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
        while True:
            diagrams_response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=' + str(page) + '&resultsPerPage=50')
            assert diagrams_response.status_code == 200
            diagrams_response_filters = diagrams_response.json()["filters"]
        #    print ("all filters json: " + str(diagrams_response_filters))
            page = page + 1

            if len(diagrams_response_filters) ==0:
                break

            for filter in diagrams_response_filters:
        #        print(filter)
                filter_id = str (filter['filterKey'])
                print(filter_id)
                permission_response = session.get('/rest/api/2/filter/' + filter_id + '/permission')
        #        print('filter json: ' + str(permission_response.json()))
                for sharePer in permission_response.json():
                    if sharePer['type']=='project':
                        if sharePer['project']['id'] in projectIdList   :
                            filterKeyList.append(filter_id)
                            exit = 1
                            break

        print(str(filterKeyList))


        with open(out_file_path, "a") as f:
            #print( diagrams_response.json() );
            for filterKey in filterKeyList:
                print(filterKey)
                for c in range(0, 10):
                    diagramId = create_diagram(session, filterKey)
                    diagrams_delete_request ='/rest/dependency-map/1.0/diagram/' + diagramId
                    f.write(diagrams_delete_request)
                    f.write("\n")
        f.close()

def create_diagram(session, filterKey):
        # Get filter key
        HOSTNAME = os.environ.get('application_hostname')

        # Get field
        diagrams_response = session.get('/rest/dependency-map/1.0/field?searchTerm=&page=0&resultsPerPage=25')
        assert diagrams_response.status_code == 200
        field= diagrams_response.json()["fields"][1]["id"]
        print(field)

        # Get field
        diagrams_response = session.get('/rest/dependency-map/1.0/field?searchTerm=&page=0&resultsPerPage=25')
        assert diagrams_response.status_code == 200
        field2= diagrams_response.json()["fields"][8]["id"]
        print(field)

        # Get user
        diagrams_response = session.get('/rest/dependency-map/1.0/user')
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]
        print("User key: " + userKey)

        # Create diagram
        payload ={ 'name':"A100", 'author':userKey,
                   'lastEditedBy':userKey, 'layoutId':2, 'filterKey': filterKey,
                   'boxColorFieldKey': field, 'groupedLayoutFieldKey': field,
                   'matrixLayoutHorizontalFieldKey': field, 'matrixLayoutVerticalFieldKey': field2}

        diagram_response = session.post('/rest/dependency-map/1.0/diagram',
                                        json=payload)
        assert diagram_response.status_code == 200
        diagramId = str(diagram_response.json()["id"])
        print("New diagram id: " + diagramId)

        # Create linkConfig
        payload = { 'diagramId': diagramId, 'linkKey': 10000, 'visible': True, 'dashType': 0, 'width': 0, 'colorPaletteEntryId': 20}

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
        payload = {"diagramId":diagramId,"fieldId":"status","fieldOptionId":fieldOptionId,"colorPaletteEntryId": colorPaletteEntryId}
        diagrams_response = session.post('/rest/dependency-map/1.0/boxColor', json=payload)
        assert diagrams_response.status_code == 200
        print( diagrams_response.json() )
        #boxColorResource = diagrams_response.json()['id']





