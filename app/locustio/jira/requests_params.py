# TODO refactor requests_params (this) to ojects approach. Class with params for each action

TEXT_HEADERS = {
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }

ADMIN_HEADERS = {
        'Accept-Language': 'en-US,en;q=0.5',
        'X-AUSERNAME': 'admin',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*'
    }
NO_TOKEN_HEADERS = {
    "Accept-Language": "en-US,en;q=0.5",
    "X-Requested-With": "XMLHttpRequest",
    "__amdModuleName": "jira/issue/utils/xsrf-token-header",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Atlassian-Token": "no-check"
}

LOGIN_BODY = {
        'os_username': '',
        'os_password': '',
        'os_destination': '',
        'user_role': '',
        'atl_token': '',
        'login': 'Log in'
    }
# login
ATL_TOKEN_PATTERN_LOGIN = r'name="atlassian-token" content="(.+?)">'


# browse_issue
ISSUE_ID_PATTERN = r'id="key-val" rel="(.+?)">'
PROJECT_AVATAR_ID_PATTERN = r'projectavatar\?avatarId\=(.+?)" '
EDIT_ALLOWED_PATTERN = "secure\/EditLabels\!default"
ASSERT_ISSUE_KEY = f'<meta name="ajs-issue-key" content="issuekey">'
BROWSE_PROJECT_PAYLOAD = {"id":"com.atlassian.jira.jira-projects-issue-navigator:sidebar-issue-navigator"}


# create_issue
OPEN_QUICK_CREATE_URL = '/secure/QuickCreateIssue!default.jspa?decorator=none'

ATL_TOKEN_PATTERN_CREATE_ISSUE = '"atl_token":"(.+?)"'
FORM_TOKEN_PATTERN = '"formToken":"(.+?)"'
ISSUE_TYPE_PATTERN = '\{&quot;label&quot;:&quot;Story&quot;,&quot;value&quot;:&quot;([0-9]*)&quot;'
PROJECT_ID_PATTERN = r'class=\\"project-field\\" value=\\"(.+?)\\"'
RESOLUTION_DONE_PATTERN = r'<option value=\\"([0-9]*)\\">\\n            Done\\n'
FIELDS_TO_RETAIN_PATTERN = '"id":"([a-z]*)","label":"[A-Za-z0-9\- ]*","required":(false|true),'
CUSTOM_FIELDS_TO_RETAIN_PATTERN = '"id":"customfield_([0-9]*)","label":"[A-Za-z0-9\- ]*","required":(false|true),'

ASSERT_STRING_CREATE_ISSUE = '"id":"project","label":"Project"'

USERPREFERENCES_PAYLOAD = {"useQuickForm": False, "fields": ["summary", "description",
                                                             "priority", "versions", "components"],
                           "showWelcomeScreen": True}
CREATED_ISSUE_KEY_PATTERN = '"issueKey":"(.+?)"'


# search_jql
PAYLOAD_ISSUE_TABLE = {"startIndex": "0",
                       "jql": "order by created DESC",
                       "layoutKey": "split-view",
                       "filterId": "-4"
                       }
ISSUE_IDS_PATTERN = '"issueIds":\[([0-9\, ]*)\]'
SEARCH_JQL_ISSUE_KEY_PATTERN = '\"table\"\:\[\{\"id\"\:(.+?)\,\"key\"\:\"(.+?)\"'
SEARCH_JQL_ISSUE_ID_PATTERN = '\"table\"\:\[\{\"id\"\:(.+?)\,'
SEARCH_JQL_EDIT_ALLOW = 'secure/EditLabels!default'

# view_project_summary
VIEW_PROJECT_SUMMARY_X_ST_PATTERN = ';st=(.+?)&'

# edit_issue
EDIT_ISSUE_TYPE_PATTERN = 'name="issuetype" type="hidden" value="(.+?)"'
EDIT_ISSUE_ATL_TOKEN_PATTERN = 'atl_token=(.+?)"'
EDIT_ISSUE_SUMMARY_PATTERN = 'name="summary" type="text" value="(.+?)"'
EDIT_ISSUE_PRIORITY_PATTERN = 'selected="selected" data-icon="(.+?)" value="(.+?)">'
EDIT_ISSUE_ASSIGNEE_REPORTER_PATTERN = '<select id="assignee" (.+?)Automatic</option><option value="(.+?)" ' \
                                       '(.+?)<option selected="selected" value="(.+?)"'
EDIT_ISSUE_REPORTER_PATTERN = 'assignee.*<option selected="selected" value="(.+?)"'
EDIT_ISSUE_RESOLUTION_PATTERN = '<option selected="selected" value="(.+?)">\n(.+?)Done'
EDIT_ISSUE_LAST_VISITED_BODY = {"id": "com.atlassian.jira.jira-projects-issue-navigator:sidebar-issue-navigator"}


# Add comment
ADD_COMMENT_FORM_TOKEN_PATTERN = 'name="formToken"\s*type="hidden"\s*value="(.+?)"'

# Browse projects
BROWSE_PROJECTS_ASSERTION_STRING = 'WRM._unparsedData["com.atlassian.jira.project.browse:projects"]="'


# Browse kanban boards
BROWSE_KANBAN_BOARDS_PROJECT_KEY = '\["project-key"\]=\"\\\\"(.+?)\\\\""'  #'\["project-key"\]="\\\"(.+?)\\\"'
BROWSE_KANBAN_BOARDS_PROJECT_ID = '\["project-id"\]=\"(.+?)\"'
BROWSE_KANBAN_BOARDS_PROJECT_PLAN = 'com.pyxis.greenhopper.jira:project-sidebar-(.+?)-(.+?)"'


# Error messages
ERR_TOKEN_NOT_FOUND = 'Atlassian token not found in login requests'
ERR_CREATE_ISSUE = 'Issue was not created'
ERR_VIEW_PROJECT_SUMMARY = 'Project not found'
ERR_EDIT_ISSUE = 'Issue not found'
