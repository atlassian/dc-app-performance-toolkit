import requests
from fixtures import session
import os

class TestGetFiler:
    def test_get_filter(self, session):
        # request list of diagrams using the session id
       HOSTNAME = os.environ.get('application_hostname')
       diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25')
       filters = diagrams_response.json()["filters"]
       assert diagrams_response.status_code == 200
       print( filters)
