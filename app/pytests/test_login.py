import requests

class TestLogin:
    def test_login(self):
        session = requests.session()

        # authenticate and get a session id
        auth_response = session.post('http://localhost:8080/rest/auth/1/session',
            json={ "username": "admin", "password": "admin" })
        assert auth_response.status_code == 200

        # request list of diagrams using the session id
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200
        assert diagrams_response.json()["total"] >= 0
