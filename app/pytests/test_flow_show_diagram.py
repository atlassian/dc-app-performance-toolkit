import requests
import pytest
import time
from fixtures import session

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

_project_id = '10000'
_diagram_id = '0'

@pytest.fixture(scope="session")
def create_data(scope="session"):
    print("start fixture create data")
    session = requests.session()
    auth_response = session.post('http://localhost:8080/rest/auth/1/session',
                                 json={ "username": "admin", "password": "admin" })
    global _project_id
    global _diagram_id

    ##################################################################################################
    #Create Diagram
    #################################################################################################
    # Get filter key
    diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
    assert diagrams_response.status_code == 200
    filterKey= str(diagrams_response.json()["filters"][1]["filterKey"])

    # Get field
    diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/field?searchTerm=&page=0&resultsPerPage=25')
    assert diagrams_response.status_code == 200
    field= diagrams_response.json()["fields"][0]["id"]

    # Create diagram
    payload ={ 'name':"D100", 'author':'admin',
       'lastEditedBy':'admin', 'layoutId':0, 'filterKey': filterKey,
        'boxColorFieldKey': field, 'groupedLayoutFieldKey': field,
        'matrixLayoutHorizontalFieldKey': 'fixVersions', 'matrixLayoutVerticalFieldKey': 'fixVersions'}

    diagrams_response = session.post('http://localhost:8080/rest/dependency-map/1.0/diagram',
        json=payload)
    assert diagrams_response.status_code == 200
    diagramKey = str(diagrams_response.json()['id'])
    _diagram_id= diagramKey
    print("Nytt diagram med id="  + diagramKey )


    #update box colore resource entry, created if not exists.
    payload = {"diagramId":diagramKey,"fieldId":"priority","fieldOptionId":1,"colorPaletteEntryId":5}
    diagrams_response = session.post('http://localhost:8080/rest/dependency-map/1.0/boxColor',
        json=payload)
    assert diagrams_response.status_code == 200
    print( diagrams_response.json() )

    #######################################################
    # Creae linkConfig
    #######################################################

    #JIRA Get list of available link types
    diagrams_response = session.get('http://localhost:8080/rest/api/2/issueLinkType')
    issueLinkTypeId = diagrams_response.json()['issueLinkTypes'][0]['id']
    print("issueLinkTypeId=" + issueLinkTypeId)

    # Create linkConfig
    payload = { 'diagramId': diagramKey, 'linkKey': issueLinkTypeId, 'visible': True, 'dashType': 0, 'width': 0, 'colorPaletteEntryId': 5}

    diagrams_response = session.post('http://localhost:8080/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramKey,
        json=payload)
    assert(diagrams_response.status_code == 200)
    newLinkConfig = diagrams_response.json()
    linkConfigId = str(newLinkConfig["id"])
    print("linkConfigId=" + linkConfigId)

    session.close()

    yield _diagram_id  # provide the fixture value
    session = requests.session()
    auth_response = session.post('http://localhost:8080/rest/auth/1/session',
                             json={ "username": "admin", "password": "admin" })
    diagrams_response2 = session.delete('http://localhost:8080/rest/dependency-map/1.0/diagram/' + _diagram_id)
    assert diagrams_response2.status_code == 200
    print("Deleted diagram id=" + _diagram_id)


class TestChangeLinkConfig:
    def test_show_diagram(self, create_data, session):
        start = time.time()
        #Get all diagrams
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200

        #JIRA Get project with everything in it
        diagrams_response = session.get('http://localhost:8080/rest/api/2/search?jql=project+%3D+' + _project_id + '+ORDER+BY+Rank+ASC&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200
        #print(diagrams_response.json());

        # Get field priority
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/field/priority')
        assert diagrams_response.status_code == 200

        # Get field fixVersion
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/field/fixVersions')
        assert diagrams_response.status_code == 200

        #Get color palet entries
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/colorPaletteEntry?palettId=' + '0')
        assert diagrams_response.status_code == 200
        colorPaletteEntryId =  diagrams_response.json() [-1]["id"]
    #    print("colorPaletteEntryId=" + str(colorPaletteEntryId))

        #Get color palet entries
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/colorPaletteEntry?palettId=' + '1')
        assert diagrams_response.status_code == 200
        colorPaletteEntryId =  diagrams_response.json() [-1]["id"]
    #    print("colorPaletteEntryId=" + str(colorPaletteEntryId))

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/boxColor?diagramId=' + _diagram_id + '&fieldId=priority&fieldOptionId=1')
        assert diagrams_response.status_code == 200
        value = diagrams_response.text
    #    if not value:
    #        print( "No response value fieldId 1")
    #    else:
    #        print( diagrams_response.json() )

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/boxColor?diagramId=' + _diagram_id + '&fieldId=priority&fieldOptionId=2')
        assert diagrams_response.status_code == 200
        value = diagrams_response.text
    #    if not value:
    #        print( "No response value fieldId 2")
    #    else:
    #       print( diagrams_response.json() )

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/boxColor?diagramId=' + _diagram_id + '&fieldId=priority&fieldOptionId=3')
        assert diagrams_response.status_code == 200
        value = diagrams_response.text
    #    if not value:
    #        print( "No response value fieldId 3")
    #    else:
    #        print( diagrams_response.json() )

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/boxColor?diagramId=' + _diagram_id + '&fieldId=priority&fieldOptionId=4')
        assert diagrams_response.status_code == 200
        value = diagrams_response.text
    #    if not value:
    #        print( "No response value fieldId 4")
    #    else:
    #        print( diagrams_response.json() )

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/boxColor?diagramId=' + _diagram_id + '&fieldId=priority&fieldOptionId=5')
        assert diagrams_response.status_code == 200
        value = diagrams_response.text
    #    if not value:
    #        print( "No response value fieldId 5")
    #    else:
    #        print( diagrams_response.json() )

        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/boxColor?diagramId=' + _diagram_id + '&fieldId=priority&fieldOptionId=-1')
        assert diagrams_response.status_code == 200
        value = diagrams_response.text
    #    if not value:
    #        print( "No response value fieldId -1")
    #    else:
    #        print( diagrams_response.json() )

        #JIRA Get list of available fileds
        diagrams_response = session.get('http://localhost:8080/rest/api/2/field')
        assert diagrams_response.status_code == 200
    #    value = diagrams_response.json()[0]
    #    content = diagrams_response.text
    #    if not value:
    #        print( "No response value field")
    #    else:
    #        print(value)

        #JIRA Get list of available link types
        diagrams_response = session.get('http://localhost:8080/rest/api/2/issueLinkType')
        assert diagrams_response.status_code == 200
        issueLinkTypeId = diagrams_response.json()['issueLinkTypes'][0]['id']
    #    print("issueLinkTypeId=" + issueLinkTypeId)

        #Get all link configs
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/linkConfig?diagramId=' + _diagram_id)
    #    print( diagrams_response.json())

        end = time.time()
        print ("Test duration: " + str(end-start))








             