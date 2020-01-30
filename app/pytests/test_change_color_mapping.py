import requests
import json

class TestChangeColorMapping:
    def test_create_color_mapping(self):
        # authenticate and get a session id
        auth_response = requests.post('http://localhost:8080/rest/auth/1/session',
            json={ "username": "admin", "password": "admin" })
        assert auth_response.status_code == 200
        session_id = auth_response.json()['session']['value']

        # Create diagram
        payload ={ 'name':"D100", 'author':'admin', 
           'lastEditedBy':'admin', 'layoutId':0, 'filterKey': 10000, 
            'boxColorFieldKey': "priority", 'groupedLayoutFieldKey': "priority", 
            'matrixLayoutHorizontalFieldKey': 'fixVersions', 'matrixLayoutVerticalFieldKey': 'fixVersions'}        
            
        diagrams_response = requests.post('http://localhost:8080/rest/dependency-map/1.0/diagram',           
            json=payload,
            cookies=dict(JSESSIONID=session_id))
        assert diagrams_response.status_code == 200    
        newDiagram = diagrams_response.json()
        diagramId = str(newDiagram["id"])
        print('diagramid=' +diagramId)
         
        # Get all priorities
        diagrams_response = requests.get('http://localhost:8080/rest/dependency-map/1.0/fieldOption/priority',
            cookies=dict(JSESSIONID=session_id)) 
        assert diagrams_response.status_code == 200            
        priorityItem = diagrams_response.json()[4]
        priorityItemId = str(priorityItem['id'])
        print('priorityItemId=' + priorityItemId)
        
        #Get colore palete entry for diagram for field=priority option=5 
        diagrams_response = requests.get('http://localhost:8080/rest/dependency-map/1.0/boxColor?diagramId=' + diagramId + '&fieldId=priority&fieldOptionId=' + priorityItemId,
            cookies=dict(JSESSIONID=session_id)) 
        assert diagrams_response.status_code == 200            
        value = diagrams_response.text
        if not value:
           print( "No response value")
        else:
           print( diagrams_response.json() ) 

        #create box coloure resource entry
        payload = {"diagramId":diagramId,"fieldId":"priority","fieldOptionId":priorityItemId,"colorPaletteEntryId":4}
        diagrams_response = requests.post('http://localhost:8080/rest/dependency-map/1.0/boxColor',
            json=payload,
            cookies=dict(JSESSIONID=session_id)) 
        assert diagrams_response.status_code == 200
        print( diagrams_response.json() )
        boxColorResource = diagrams_response.json()['id']
        
        #update box coloure resource entry, created if not exists.
        payload = {"id":boxColorResource,"diagramId":diagramId,"fieldId":"priority","fieldOptionId":priorityItemId,"colorPaletteEntryId":5}
        diagrams_response = requests.put('http://localhost:8080/rest/dependency-map/1.0/boxColor',
            json=payload,
            cookies=dict(JSESSIONID=session_id)) 
        assert diagrams_response.status_code == 200
        print( diagrams_response.json() )
        
        
    
           
        
        
              
        
 
