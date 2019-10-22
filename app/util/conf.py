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
        self.application_postfix = obj['settings']['env']['application_postfix']
        self.admin_login = obj['settings']['env']['admin_login']
        self.admin_password = obj['settings']['env']['admin_password']
        self.concurrency = obj['settings']['env']['concurrency']

    def __repr__(self):
        return f'application_hostname = {self.application_hostname!r}\n' \
               f'application_protocol = {self.application_protocol!r}\n' \
               f'application_port = {self.application_port!r}\n' \
               f'application_postfix = {self.application_postfix!r}\n' \
               f'admin_login = {self.admin_login!r}\n' \
               f'admin_password = {self.admin_password!r}\n' \
               f'concurrency = {self.concurrency!r}\n'


JIRA_SETTINGS = JiraSettings()
print(JIRA_SETTINGS.application_postfix)
