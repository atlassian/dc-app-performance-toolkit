import requests
from fixtures import session

class TestCopy:
    def test_copy(self, session):

        # request list of diagrams using the session id
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200
        total = diagrams_response.json()["total"];
        values = diagrams_response.json()["values"];
        diagram1 = values[0];
        id1= str(diagram1["id"])
        print( id1)
        print( diagrams_response.json() ); 
        
        #create a copy of the diagram
        diagrams_response = session.post('http://localhost:8080/rest/dependency-map/1.0/diagram/duplicate/' + id1 )
        assert diagrams_response.status_code == 200
        print( diagrams_response.json() );
