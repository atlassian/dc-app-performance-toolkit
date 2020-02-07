import requests
from fixtures import session

class TestDelete:
    def test_delete_diagram(self, session):
        # Prepare
        # request list of diagrams using the session id
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200
        total = diagrams_response.json()["total"];
        values = diagrams_response.json()["values"];
        diagram1 = values[0];
        id1= diagram1["id"]
        idString = str(id1)
        print("Diagram to copy id: " + idString)
        # create a copy       
        diagrams_response = session.post('http://localhost:8080/rest/dependency-map/1.0/diagram/duplicate/' + idString)
        assert diagrams_response.status_code == 200

        # Prepare
        # get all diagrams, choose the last
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200
        total = diagrams_response.json()["total"];
        values = diagrams_response.json()["values"];
        diagram1 = values[total-1];
        id1= diagram1["id"]
        idString = str(id1)
        print("New diagram id: "+ idString)

        #remove
        diagrams_response2 = session.delete('http://localhost:8080/rest/dependency-map/1.0/diagram/' + idString)
        assert diagrams_response2.status_code == 200
        print("Diagram removed")
        #print( diagrams_response.json() );

        #get all diagrams after delete
        diagrams_response = session.get('http://localhost:8080/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50')
        assert diagrams_response.status_code == 200

        
 
