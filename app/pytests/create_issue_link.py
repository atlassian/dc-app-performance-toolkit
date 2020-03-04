import requests
from conftest import print_timing
from fixtures import session
from fixtures import base_url
from maxfreq import max_freq
from conftest import print_in_shell
from conftest import getRandomProjectId

import os

#POST /rest/api/2/issueLink
#GET /rest/api/2/issue/10002



class TestCreateLink:
    @print_timing
    def test_create_issue_link(self, base_url, session):
        #JIRA Get project id
        diagrams_response = session.get('/rest/api/2/project')
        assert diagrams_response.status_code == 200

        # Get project id from the list of projects we shall use, saved in a file
        projectId=getRandomProjectId()
        print_in_shell('projectId:' +  projectId);
        
        #JIRA Get list of available issues
        diagrams_response = session.get('/rest/api/2/search?jql=project=' + projectId)
        assert diagrams_response.status_code == 200
        if len(diagrams_response.json()['issues']) > 9:
            issueId1 = diagrams_response.json()['issues'][0]['id']
            issueKey1 = diagrams_response.json()['issues'][0]['key']
            issueId2 = diagrams_response.json()['issues'][9]['id']
            print_in_shell ('issueId1=' + issueId1 + ' key=' + issueKey1 + ' issueId2=' + issueId2)
            #JIRA Get list of available link types
            diagrams_response = session.get('/rest/api/2/issueLinkType')
            issueLinkTypeId = diagrams_response.json()['issueLinkTypes'][0]['id']
            print_in_shell("issueLinkTypeId=" + issueLinkTypeId)

            #JIRA Get new issue links id
            diagrams_response = session.get('/rest/api/2/issue/' + issueId1)
            issueLinks = diagrams_response.json()['fields']['issuelinks']
          #  print(issueLinks)
            print("Before")
            print(issueLinks[0]['id'])
            print(issueLinks[-1]['id'])

            #JIRA create link
            #print (issueId1);
            #print(issueId2)
            payload = { 'type': { 'id': issueLinkTypeId},  #blocks?
                         'inwardIssue': { 'id': issueId2 },
                         'outwardIssue': { 'id': issueId1}}
            diagrams_response = session.post('/rest/api/2/issueLink',
                json= payload)
            assert diagrams_response.status_code == 201
            print_in_shell("issue created")

            #JIRA Get new issue links id
            diagrams_response = session.get('/rest/api/2/issue/' + issueId1)
            issueLinks = diagrams_response.json()['fields']['issuelinks']
            firstIssueLinksId = issueLinks[0]['id']
            firstIssueLinkSelf = issueLinks[0]['self']


           # print(issueLinks)
            print(issueLinks[0]['id'])
            print(issueLinks[-1]['id'])
            #diagrams_response = session.get(firstIssueLinkSelf)
            #assert diagrams_response.status_code == 200






        
             