import requests
from conftest import print_timing
from fixtures import session
from maxfreq import max_freq
from conftest import print_in_shell

import os

#POST /rest/api/2/issueLink
#GET /rest/api/2/issue/10002



class TestCreateLink:
    @max_freq(500/3600)
    @print_timing
    def test_create_issue_link(self, session):
        #JIRA Get project id
        HOSTNAME = os.environ.get('application_hostname')
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/api/2/project')
        assert diagrams_response.status_code == 200 
        projectId = diagrams_response.json()[1]['id']        
        print_in_shell('projectId:' +  projectId);
        
        #JIRA Get list of available issues
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/api/2/search?jql=project=' + projectId)
        assert diagrams_response.status_code == 200       
        issueId1 = diagrams_response.json()['issues'][0]['id']
        issueKey1 = diagrams_response.json()['issues'][0]['key']
        issueId2 = diagrams_response.json()['issues'][9]['id']
        print_in_shell ('issueId1=' + issueId1 + ' key=' + issueKey1 + ' issueId2=' + issueId2)
        #JIRA Get list of available link types
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/api/2/issueLinkType')
        issueLinkTypeId = diagrams_response.json()['issueLinkTypes'][0]['id']  
        print_in_shell("issueLinkTypeId=" + issueLinkTypeId)

        ####
        #JIRA create link                 
        payload = { 'type': { 'id': issueLinkTypeId},  #blocks?
                     'inwardIssue': { 'id': issueId2 },   
                     'outwardIssue': { 'id': issueId1}}                            
        diagrams_response = session.post('http://'  + HOSTNAME + ':8080/rest/api/2/issueLink',
            json= payload)
        assert diagrams_response.status_code == 201
        print_in_shell("issue created")

        ###
        #JIRA Get new issue links id
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/api/2/issue/' + issueId1)
       # diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/api/2/issue/SCRUM-128')
        issueLinks = diagrams_response.json()['fields']['issuelinks']
        firstIssueLinksId = issueLinks[0]['id']
        firstIssueLinkSelf = issueLinks[0]['self']
        #lastIssueLinksId = issueLinks[-1]['id']

        diagrams_response = session.get(firstIssueLinkSelf)
        assert diagrams_response.status_code == 200

        print_in_shell("Deleted issueLinksId=" + firstIssueLinksId);
        diagrams_response = session.delete('http://'  + HOSTNAME + ':8080/rest/api/latest/issueLink/' + firstIssueLinksId)
        assert diagrams_response.status_code == 204




        
             