import requests
from fixtures import session
import os

#POST /rest/api/2/issueLink
#GET /rest/api/2/issue/10002



class TestCreateLink:
    def test_create_issue_link(self, session):
        #JIRA Get project id
        HOSTNAME = os.environ.get('application_hostname')
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/api/2/project')
        assert diagrams_response.status_code == 200 
        projectId = diagrams_response.json()[1]['id']        
        print('projectId:' +  projectId);
        
        #JIRA Get list of available issues
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/api/2/search?jql=project=' + projectId)
        assert diagrams_response.status_code == 200       
        issueId1 = diagrams_response.json()['issues'][0]['id']
        issueKey1 = diagrams_response.json()['issues'][0]['key']
        issueId2 = diagrams_response.json()['issues'][9]['id']
        print ('issueId1=' + issueId1 + ' key=' + issueKey1 + ' issueId2=' + issueId2)      
        #JIRA Get list of available link types
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/api/2/issueLinkType')
        issueLinkTypeId = diagrams_response.json()['issueLinkTypes'][0]['id']  
        print("issueLinkTypeId=" + issueLinkTypeId)

        ####
        #JIRA create link                 
        payload = { 'type': { 'id': issueLinkTypeId},  #blocks?
                     'inwardIssue': { 'id': issueId2 },   
                     'outwardIssue': { 'id': issueId1}}                            
        diagrams_response = session.post('http://'  + HOSTNAME + ':8080/rest/api/2/issueLink',
            json= payload)
        assert diagrams_response.status_code == 201
        print("issue created")

        ###
        #JIRA Get new issue links id
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/api/2/issue/' + issueKey1)
        issueLinks = diagrams_response.json()['fields']['issuelinks']
        issueLinksId = issueLinks[0]['id']
        print("New issue Links Id=" + issueLinksId);
        
        #JIRA Delete issue link
       # diagrams_response = requests.delete('http://'  + HOSTNAME + ':8080/rest/api/2/issueLink/' + issueLinksId,
       #     json= payload,
       #    cookies=dict(JSESSIONID=session_id))
       # assert diagrams_response.status_code == 204
       #print("Deleted issueLinksId=" + issueLinksId);
        
             