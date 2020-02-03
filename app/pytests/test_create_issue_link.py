import requests

class TestCreateLink:
    def test_copy(self):
        # authenticate and get a session id
        auth_response = requests.post('http://localhost:8080/rest/auth/1/session',
            json={ "username": "admin", "password": "admin" })
        assert auth_response.status_code == 200
        session_id = auth_response.json()['session']['value']
           
        #JIRA Get project id
        diagrams_response = requests.get('http://localhost:8080/rest/api/2/project',
            cookies=dict(JSESSIONID=session_id))
        assert diagrams_response.status_code == 200 
        projectId = diagrams_response.json()[1]['id']        
        print('projectId:' +  projectId);
        
        #JIRA Get list of available issues
        diagrams_response = requests.get('http://localhost:8080/rest/api/2/search?jql=project=' + projectId,
            cookies=dict(JSESSIONID=session_id))
        assert diagrams_response.status_code == 200       
        issueId1 = diagrams_response.json()['issues'][0]['id']
        issueKey1 = diagrams_response.json()['issues'][0]['key']
        issueId2 = diagrams_response.json()['issues'][15]['id']
        print ('issueId1=' + issueId1 + ' key=' + issueKey1 + ' issueId2=' + issueId2)      
        #JIRA Get list of available link types
        diagrams_response = requests.get('http://localhost:8080/rest/api/2/issueLinkType',
            cookies=dict(JSESSIONID=session_id))
        issueLinkTypeId = diagrams_response.json()['issueLinkTypes'][0]['id']  
        print("issueLinkTypeId=" + issueLinkTypeId);
      
        #JIRA create link                 
        payload = { 'type': { 'id': issueLinkTypeId},  #blocks?
                     'inwardIssue': { 'id': issueId2 },   
                     'outwardIssue': { 'id': issueId1}}                            
        diagrams_response = requests.post('http://localhost:8080/rest/api/2/issueLink',
            json= payload,
            cookies=dict(JSESSIONID=session_id))
        assert diagrams_response.status_code == 201
        print("issue created");
         
        #JIRA Get new issue links id
        diagrams_response = requests.get('http://localhost:8080/rest/api/2/issue/' + issueKey1,
            cookies=dict(JSESSIONID=session_id))
        issueLinks = diagrams_response.json()['fields']['issuelinks']
        issueLinksId = issueLinks[0]['id']
        print("New issue Links Id=" + issueLinksId);
        
        ####################################
        # Get filter key
        diagrams_response = requests.get('http://localhost:8080/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25',
            cookies=dict(JSESSIONID=session_id))
        assert diagrams_response.status_code == 200
        filterKey= str(diagrams_response.json()["filters"][1]["filterKey"])
        print(filterKey)
        
        # Get field
        diagrams_response = requests.get('http://localhost:8080/rest/dependency-map/1.0/field?searchTerm=&page=0&resultsPerPage=25',
            cookies=dict(JSESSIONID=session_id))
        assert diagrams_response.status_code == 200
        field= diagrams_response.json()["fields"][0]["id"]
        print(field)

        # Get user        
        diagrams_response = requests.get('http://localhost:8080/rest/dependency-map/1.0/user',
            cookies=dict(JSESSIONID=session_id))
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]
        print(userKey)
        
        # Create diagram
        payload ={ 'name':"D100", 'author':'admin', 
           'lastEditedBy':'admin', 'layoutId':0, 'filterKey': filterKey, 
            'boxColorFieldKey': field, 'groupedLayoutFieldKey': field, 
            'matrixLayoutHorizontalFieldKey': 'fixVersions', 'matrixLayoutVerticalFieldKey': 'fixVersions'}               
      
        diagrams_response = requests.post('http://localhost:8080/rest/dependency-map/1.0/diagram',           
            json=payload,
            cookies=dict(JSESSIONID=session_id))
        assert diagrams_response.status_code == 200
        diagramKey = str(diagrams_response.json()['id'])
        print("Nytt diagram med id="  + diagramKey )
        print(diagrams_response.json())
               
        # Get diagram
        diagrams_response = requests.get('http://localhost:8080/rest/dependency-map/1.0/diagram/' + diagramKey,           
            cookies=dict(JSESSIONID=session_id))
            
        diagramId = diagrams_response.json()['id'];
        fetchedDiagramKey = str(diagramId);
        assert diagramKey==fetchedDiagramKey
        print("Get diagram succeded:" + diagramKey)
        
        #update box coloure resource entry, created if not exists.
        payload = {"diagramId":diagramId,"fieldId":"priority","fieldOptionId":1,"colorPaletteEntryId":5}
        diagrams_response = requests.post('http://localhost:8080/rest/dependency-map/1.0/boxColor',
            json=payload,
            cookies=dict(JSESSIONID=session_id)) 
        assert diagrams_response.status_code == 200
        print( diagrams_response.json() )
        
        #JIRA Get list of available link types
        diagrams_response = requests.get('http://localhost:8080/rest/api/2/issueLinkType',
            cookies=dict(JSESSIONID=session_id))
        issueLinkTypeId = diagrams_response.json()['issueLinkTypes'][0]['id']  
        print("issueLinkTypeId=" + issueLinkTypeId)       
        
        # Create linkConfig
        payload = { 'diagramId': diagramKey, 'linkKey': issueLinkTypeId, 'visible': True, 'dashType': 0, 'width': 0, 'colorPaletteEntryId': 5}      
        
        diagrams_response = requests.post('http://localhost:8080/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramKey,           
            json=payload,
            cookies=dict(JSESSIONID=session_id))
        assert(diagrams_response.status_code == 200)
        newLinkConfig = diagrams_response.json()
        linkConfigId = str(newLinkConfig["id"])
        print("linkConfigId=" + linkConfigId)
        
        # GET /rest/api/2/search?jql=project+%3D+SCRUM+ORDER+BY+Rank+ASC&startAt=0&maxResults=50
        # /rest/dependency-map/1.0/colorPaletteEntry
        # /rest/dependency-map/1.0/colorPaletteEntry?paletteId=0
        # GET /rest/dependency-map/1.0/boxColor?diagramId=2&fieldId=priority&fieldOptionId=3 
        # GET /rest/api/2/issueLinkType
        # GET /rest/dependency-map/1.0/linkConfig?diagramId=2
        ########################
        
        #JIRA Get project with everything in it
        diagrams_response = requests.get('http://localhost:8080/rest/api/2/search?jql=project+%3D+' + projectId + '+ORDER+BY+Rank+ASC&startAt=0&maxResults=50',
            cookies=dict(JSESSIONID=session_id)) 
        assert diagrams_response.status_code == 200             
        #print(diagrams_response.json()); 
        
        #Get all color palet entries
        diagrams_response = requests.get('http://localhost:8080/rest/dependency-map/1.0/colorPaletteEntry',
            cookies=dict(JSESSIONID=session_id))       
        assert diagrams_response.status_code == 200
        colorPaletteId =  str(diagrams_response.json() [0]["id"])   
  
        #Get color palet entries
        diagrams_response = requests.get('http://localhost:8080/rest/dependency-map/1.0/colorPaletteEntry?palettId=' + colorPaletteId,
            cookies=dict(JSESSIONID=session_id))       
        assert diagrams_response.status_code == 200 
        colorPaletteEntryId =  diagrams_response.json() [-1]["id"] 
        print("colorPaletteEntryId=" + str(colorPaletteEntryId))
        
        #Get boxcolor, värden när dessa är explicit ändrade.
        diagrams_response = requests.get('http://localhost:8080/rest/dependency-map/1.0/boxColor?diagramId=' + fetchedDiagramKey + '&fieldId=priority&fieldOptionId=1',
            cookies=dict(JSESSIONID=session_id))       
        assert diagrams_response.status_code == 200 
        value = diagrams_response.text
        if not value:
           print( "No response value")
        else:
           print( diagrams_response.json() )         
                   		            
        
        #JIRA Get list of available link types
        diagrams_response = requests.get('http://localhost:8080/rest/api/2/issueLinkType',
            cookies=dict(JSESSIONID=session_id))
        issueLinkTypeId = diagrams_response.json()['issueLinkTypes'][0]['id']  
        print("issueLinkTypeId=" + issueLinkTypeId)       
        
        
        # Get all link configs
        diagrams_response = requests.get('http://localhost:8080/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramKey,           
            cookies=dict(JSESSIONID=session_id))
        print( diagrams_response.json() )
        
        #JIRA Delete issue link
       # diagrams_response = requests.delete('http://localhost:8080/rest/api/2/issueLink/' + issueLinksId,
       #     json= payload,
       #    cookies=dict(JSESSIONID=session_id))
       # assert diagrams_response.status_code == 204 
       #print("Deleted issueLinksId=" + issueLinksId);
        
             