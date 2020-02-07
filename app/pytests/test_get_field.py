import requests
from fixtures import session

class TestGetField:
    def test_get_field(self, session):
        # request list of diagrams using the session id
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/field?searchTerm=&page=0&resultsPerPage=25')
        fields = diagrams_response.json()["fields"]
        assert diagrams_response.status_code == 200
        print(fields)

