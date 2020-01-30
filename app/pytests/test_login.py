from fixtures import session

class TestLogin:
    def test_login(self, session):
        # request list of diagrams using the session id
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200
        assert diagrams_response.json()["total"] >= 0
