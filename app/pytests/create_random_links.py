from fixtures import session
from fixtures import base_url
from fixtures import nr_projects
from conftest import saveProjectCmd
import os
from os import path
import math
import random
import pathlib
from itertools import islice


basepath = path.dirname(__file__)
#CURRENT_PATH = pathlib.Path().absolute()
out_file_path = path.abspath(path.join(basepath, "deleteCreatedObjects"))

# returns the number of ways k elements can be chosen from n elements
def binom(n, k):
    return math.factorial(n) // math.factorial(k) // math.factorial(n - k)

# returns the number in an issue key
def issue_key_number(s):
    return int(s.partition("-")[2])

def get_link_type(session):
    #JIRA Get list of available link types
    issueLinkTypeId = 0
    diagrams_response = session.get('/rest/api/2/issueLinkType')
    issueLinkTypes = diagrams_response.json()['issueLinkTypes']
    for linkType in issueLinkTypes:
        print(linkType)
        if linkType["name"]=="Blocks":
            issueLinkTypeId=linkType["id"]
            break
    print(issueLinkTypeId)
    return issueLinkTypeId

class TestCreateIssueLinks:
    def test_create_issue_links(self, base_url, nr_projects, session):
        # get all projects
        projStartAt = 0

        respProj = session.get('/rest/api/latest/project',auth=('admin', 'admin'))

        issueLinkTypeId = get_link_type(session)
        assert respProj.status_code == 200
        projects = respProj.json()
        print("NR of projects: " + str(nr_projects))
        if len(projects) > nr_projects:
            projects = x = islice(projects, 0, nr_projects)
        for project in projects:
            project_key = project['key']
            saveProjectCmd( project['name'], project['key'], project['id'])
            # collect keys of all issues in this project into issue_ids
            link_percentage = 30
            issue_ids = []
            startAt = 0
            while True:
                resp = session.get(f'/rest/api/latest/search?maxResults=100&startAt={startAt}&jql=project={project_key}&fields=key')
                assert resp.status_code == 200
                result = resp.json()
                print(f"if {startAt} >= {result['total']}")
                if startAt >= result['total'] or not('issues' in result):
                    break
                issue_ids.extend(list(map(lambda issue : issue['id'], result['issues'])))
                startAt = len(issue_ids)
            if len(issue_ids)==0:
                break
            # generate link_percentage random issue pairs out of issue_ids
            # all pairs are in increasing order, to avoid link cycles
            pair_count = min(len(issue_ids) * link_percentage / 100, binom(len(issue_ids), 2)) # limit wanted number of links by theoretical maximum
            pairs = set()   # set of tuples, as tuples can be added to a set, but not lists
            while len(pairs) < pair_count:
                pair = tuple(sorted(random.sample(issue_ids, 2)))
                if pair not in pairs:
                    pairs.add(pair)
            for pair in pairs:
                print(pair)
                self.create_link(session, issueLinkTypeId, pair[0], pair[1])
        print("end")

    def create_link(self, session, issueLinkTypeId, from_issue_id, to_issue_id):
        #before
        diagrams_response = session.get('/rest/api/2/issue/' + from_issue_id)
        before_issue_links = diagrams_response.json()['fields']['issuelinks']
        before_size = len(before_issue_links)

        payload = { 'type': { 'id': issueLinkTypeId},  #blocks?
                    'inwardIssue': { 'id': to_issue_id },
                    'outwardIssue': { 'id': from_issue_id}}
        diagrams_response = session.post('/rest/api/2/issueLink',
                                     json= payload)

        print(f"created link from issue {from_issue_id} to {to_issue_id} ")

        #JIRA Get new issue links id
        diagrams_response = session.get('/rest/api/2/issue/' + from_issue_id)
        issueLinks = diagrams_response.json()['fields']['issuelinks']
        #print(issueLinks)
        if (len(issueLinks) > before_size):
            issueLinksId = 0
            for issueLink in issueLinks:
                if 'inwardIssue' in issueLink and  issueLink['inwardIssue']:
                   if  issueLink['inwardIssue']['id']==to_issue_id:
                       issueLinksId = issueLink['id']

            #issueLinksId = issueLinks[-1]['id']
            print("New issue Links Id=" + issueLinksId);
            if issueLinksId!=0:
                try:
                    with open(out_file_path, "a") as f:
                        issueLink_delete_request ='/rest/api/latest/issueLink/' + issueLinksId
                        f.write(issueLink_delete_request)
                        f.write("\n")
                        f.close()
                except IOError:
                    print("File not accessible")



#/rest/api/latest/project
# [
#   {
#     "expand": "description,lead,url,projectKeys",
#     "self": "http://localhost:8080/rest/api/2/project/10001",
#     "id": "10001",
#     "key": "DRKAN",
#     "name": "drkanban",
#     "avatarUrls": {
#       "48x48": "http://localhost:8080/secure/projectavatar?avatarId=10324",
#       "24x24": "http://localhost:8080/secure/projectavatar?size=small&avatarId=10324",
#       "16x16": "http://localhost:8080/secure/projectavatar?size=xsmall&avatarId=10324",
#       "32x32": "http://localhost:8080/secure/projectavatar?size=medium&avatarId=10324"
#     },
#     "projectTypeKey": "software"
#   },
#   {
#     "expand": "description,lead,url,projectKeys",
#     "self": "http://localhost:8080/rest/api/2/project/10000",
#     "id": "10000",
#     "key": "DRSCRUM",
#     "name": "drscrum",
#     "avatarUrls": {
#       "48x48": "http://localhost:8080/secure/projectavatar?avatarId=10324",
#       "24x24": "http://localhost:8080/secure/projectavatar?size=small&avatarId=10324",
#       "16x16": "http://localhost:8080/secure/projectavatar?size=xsmall&avatarId=10324",
#       "32x32": "http://localhost:8080/secure/projectavatar?size=medium&avatarId=10324"
#     },
#     "projectTypeKey": "software"
#   }
# ]

#/rest/api/latest/search?maxResults=2&jql=project=DRKAN&fields=key
# {
#   "expand": "schema,names",
#   "startAt": 0,
#   "maxResults": 2,
#   "total": 16,
#   "issues": [
#     {
#       "expand": "operations,versionedRepresentations,editmeta,changelog,renderedFields",
#       "id": "10038",
#       "self": "http://localhost:8080/rest/api/latest/issue/10038",
#       "key": "DRKAN-16"
#     },
#     {
#       "expand": "operations,versionedRepresentations,editmeta,changelog,renderedFields",
#       "id": "10037",
#       "self": "http://localhost:8080/rest/api/latest/issue/10037",
#       "key": "DRKAN-15"
#     }
#   ]
# }
