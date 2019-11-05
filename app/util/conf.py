import yaml

from util.project_paths import JIRA_YML, CONFLUENCE_YML


def read_yml_file(file):
    with file.open(mode='r') as file:
        return yaml.load(file, Loader=yaml.FullLoader)


class JiraSettings:

    def __init__(self):
        obj = read_yml_file(JIRA_YML)
        self.hostname = obj['settings']['env']['application_hostname']
        self.protocol = obj['settings']['env']['application_protocol']
        self.port = obj['settings']['env']['application_port']
        self.postfix = obj['settings']['env']['application_postfix'] or ""
        self.admin_login = obj['settings']['env']['admin_login']
        self.admin_password = obj['settings']['env']['admin_password']
        self.concurrency = obj['settings']['env']['concurrency']

    @property
    def server_url(self):
        return f'{self.protocol}://{self.hostname}:{self.port}{self.postfix}'


class ConfluenceSettings:

    def __init__(self):
        obj = read_yml_file(CONFLUENCE_YML)
        self.hostname = obj['settings']['env']['application_hostname']
        self.protocol = obj['settings']['env']['application_protocol']
        self.port = obj['settings']['env']['application_port']
        self.postfix = obj['settings']['env']['application_postfix'] or ""
        self.admin_login = obj['settings']['env']['admin_login']
        self.admin_password = obj['settings']['env']['admin_password']
        self.concurrency = obj['settings']['env']['concurrency']

    @property
    def server_url(self):
        return f'{self.protocol}://{self.hostname}:{self.port}{self.postfix}'


JIRA_SETTINGS = JiraSettings()
CONFLUENCE_SETTINGS = ConfluenceSettings()
