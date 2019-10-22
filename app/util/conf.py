import yaml
from app.util.project_paths import JIRA_YML


def read_yml_file(file):
    with file.open(mode='r') as file:
        return yaml.load(file, Loader=yaml.FullLoader)


class JiraSettings:

    def __init__(self):
        obj = read_yml_file(JIRA_YML)
        self.application_hostname = obj['settings']['env']['application_hostname']
        self.application_protocol = obj['settings']['env']['application_protocol']
        self.application_port = obj['settings']['env']['application_port']

    def __repr__(self):
        return f'application_hostname = {self.application_hostname!r}\napplication_protocol = {self.application_protocol!r}\n' \
    f'application_port = {self.application_port!r}'


jira_settings = JiraSettings()

