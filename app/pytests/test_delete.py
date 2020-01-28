import requests

class TestLogin:
    def test_login(self):
        # authenticate and get a session id
        auth_response = requests.post('http://localhost:8080/rest/auth/1/session',
            json={ "username": "admin", "password": "admin" })
        assert auth_response.status_code == 200
        session_id = auth_response.json()['session']['value']

        # request list of diagrams using the session id
        diagrams_response = requests.get('http://localhost:8080/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50',
            cookies=dict(JSESSIONID=session_id))
        assert diagrams_response.status_code == 200
        total = diagrams_response.json()["total"];
        values = diagrams_response.json()["values"];
        diagram1 = values[0];
        id1= diagram1["id"]
        idString = str(id1)
        print(id1)
        # create a copy       
        diagrams_response = requests.post('http://localhost:8080/rest/dependency-map/1.0/diagram/duplicate/' + idString ,
            cookies=dict(JSESSIONID=session_id))
        assert diagrams_response.status_code == 200
        # 
        diagrams_response = requests.get('http://localhost:8080/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50',
            cookies=dict(JSESSIONID=session_id))
        assert diagrams_response.status_code == 200
        total = diagrams_response.json()["total"];
        values = diagrams_response.json()["values"];
        diagram1 = values[total-1];
        id1= diagram1["id"]
        print(id1);
        idString = str(id1)
        #remove
        diagrams_response2 = requests.delete('http://localhost:8080/rest/dependency-map/1.0/diagram/' + idString,
            cookies=dict(JSESSIONID=session_id))
        assert diagrams_response2.status_code == 200

        
 
