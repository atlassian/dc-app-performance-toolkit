import json

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
# Error messages
ERR_TOKEN_NOT_FOUND = 'Atlassian token not found in login requests'
ERR_CREATE_ISSUE = 'Issue was not created'
ERR_VIEW_PROJECT_SUMMARY = 'Project not found'
ERR_EDIT_ISSUE = 'Issue not found'


class BaseResource:
    resources_file = 'locustio/jira/resources.json'
    action_name = ''

    def __init__(self):
        self.resources_json = self.read_json()
        self.body = self.action_resources()

    def read_json(self):
        with open(self.resources_file) as f:
            return json.load(f)

    def action_resources(self):
        return self.resources_json[self.action_name] if self.action_name in self.resources_json else None


class Login(BaseResource):
    action_name = 'login_and_view_dashboard'
    atl_token_pattern = r'name="atlassian-token" content="(.+?)">'
    login_body = {
        'os_username': '',
        'os_password': '',
        'os_destination': '',
        'user_role': '',
        'atl_token': '',
        'login': 'Log in'
    }


class BrowseIssue(BaseResource):
    issue_id_pattern = r'id="key-val" rel="(.+?)">'
    project_avatar_id_pattern = r'projectavatar\?avatarId\=(.+?)" '
    edit_allow_pattern = "secure\/EditLabels\!default"
    browse_project_payload = {"id": "com.atlassian.jira.jira-projects-issue-navigator:sidebar-issue-navigator"}


class ViewDashboard(BaseResource):
    action_name = 'view_dashboard'


class CreateIssue(BaseResource):
    atl_token_pattern = '"atl_token":"(.+?)"'
    form_token_pattern = '"formToken":"(.+?)"'
    issue_type_pattern = '\{&quot;label&quot;:&quot;Story&quot;,&quot;value&quot;:&quot;([0-9]*)&quot;'
    project_id_pattern = r'class=\\"project-field\\" value=\\"(.+?)\\"'
    resolution_done_pattern = r'<option value=\\"([0-9]*)\\">\\n            Done\\n'
    fields_to_retain_pattern = '"id":"([a-z]*)","label":"[A-Za-z0-9\- ]*","required":(false|true),'
    custom_fields_to_retain_pattern = '"id":"customfield_([0-9]*)","label":"[A-Za-z0-9\- ]*","required":(false|true),'
    user_preferences_payload = {"useQuickForm": False, "fields": ["summary", "description",
                                                                  "priority", "versions", "components"],
                                "showWelcomeScreen": True}
    create_issue_key_pattern = '"issueKey":"(.+?)"'
    create_issue_assertion = '"id":"project","label":"Project"'


class SearchJql(BaseResource):
    action_name = 'search_jql'
    issue_table_payload = {"startIndex": "0",
                           "jql": "order by created DESC",
                           "layoutKey": "split-view",
                           "filterId": "-4"}
    ids_pattern = '"issueIds":\[([0-9\, ]*)\]'
    issue_key_pattern = '\"table\"\:\[\{\"id\"\:(.+?)\,\"key\"\:\"(.+?)\"'
    issue_id_pattern = '\"table\"\:\[\{\"id\"\:(.+?)\,'
    edit_allow_string = 'secure/EditLabels!default'


class ViewProjectSummary(BaseResource):
    action_name = 'view_project_summary'


class EditIssue(BaseResource):
    action_name = 'edit_issue'
    issue_type_pattern = 'name="issuetype" type="hidden" value="(.+?)"'
    atl_token_pattern = 'atl_token=(.+?)"'
    issue_priority_pattern = 'selected="selected" data-icon="(.+?)" value="(.+?)">'
    issue_assigneee_reporter_pattern = '<select id="assignee" (.+?)Automatic</option><option value="(.+?)" ' \
                                       '(.+?)<option selected="selected" value="(.+?)"'
    issue_reporter_pattern = 'assignee.*<option selected="selected" value="(.+?)"'
    last_visited_body = {"id": "com.atlassian.jira.jira-projects-issue-navigator:sidebar-issue-navigator"}


class AddComment(BaseResource):
    action_name = 'add_comment'
    form_token_pattern = 'name="formToken"\s*type="hidden"\s*value="(.+?)"'
    atl_token_pattern = r'name="atlassian-token" content="(.+?)">'


class BrowseProjects(BaseResource):
    action_name = 'browse_projects'
    assertion_string = 'WRM._unparsedData["com.atlassian.jira.project.browse:projects"]="'


class ViewBoard(BaseResource):
    action_name = 'view_kanban_board'
    project_key_pattern = '\["project-key"\]=\"\\\\"(.+?)\\\\""'
    project_id_pattern = '\["project-id"\]=\"(.+?)\"'
    project_plan_pattern = 'com.pyxis.greenhopper.jira:project-sidebar-(.+?)-(.+?)"'






# # Browse kanban boards
# BROWSE_KANBAN_BOARDS_PROJECT_KEY = '\["project-key"\]=\"\\\\"(.+?)\\\\""'  #'\["project-key"\]="\\\"(.+?)\\\"'
# BROWSE_KANBAN_BOARDS_PROJECT_ID = '\["project-id"\]=\"(.+?)\"'
# BROWSE_KANBAN_BOARDS_PROJECT_PLAN = 'com.pyxis.greenhopper.jira:project-sidebar-(.+?)-(.+?)"'
#

