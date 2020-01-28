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
        id1= str(diagram1["id"])
        print( id1)
        diagrams_response = requests.post('http://localhost:8080/rest/dependency-map/1.0/diagram/duplicate/' + id1 ,
            cookies=dict(JSESSIONID=session_id))
        print(diagrams_response)
        assert diagrams_response.status_code == 200      
        
