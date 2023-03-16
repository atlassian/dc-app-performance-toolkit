import argparse
from pathlib import Path
from platform import system
from subprocess import run
from sys import version_info

import yaml

SUPPORTED_PYTHON_VERSIONS = ["3.8", "3.9", "3.10", "3.11"]

python_full_version = '.'.join(map(str, version_info[0:3]))
python_short_version = '.'.join(map(str, version_info[0:2]))
print("Python version: {}".format(python_full_version))
if python_short_version not in SUPPORTED_PYTHON_VERSIONS:
    raise SystemExit("Python version {} is not supported. "
                     "Supported versions: {}.".format(python_full_version, SUPPORTED_PYTHON_VERSIONS))

JIRA = "jira"
CONFLUENCE = "confluence"
BITBUCKET = "bitbucket"
JSM = "jsm"
CROWD = "crowd"
BAMBOO = "bamboo"
APP_DIR = Path(__file__).resolve().parents[2]
PROPERTIES = APP_DIR / "util" / "jmeter" / "jmeter.properties"
JIRA_YML = APP_DIR / "jira.yml"
CROWD_YML = APP_DIR / "crowd.yml"
CONFLUENCE_YML = APP_DIR / "confluence.yml"
BITBUCKET_YML = APP_DIR / "bitbucket.yml"
JSM_YML = APP_DIR / "jsm.yml"
BAMBOO_YML = APP_DIR / "bamboo.yml"
JIRA_JMX = APP_DIR / "jmeter" / "jira.jmx"
CROWD_JMX = APP_DIR / "jmeter" / "crowd.jmx"
BAMBOO_JMX = APP_DIR / "jmeter" / "bamboo.jmx"
CONFLUENCE_JMX = APP_DIR / "jmeter" / "confluence.jmx"
BITBUCKET_JMX = APP_DIR / "jmeter" / "bitbucket.jmx"
JSM_JMX_AGENTS = APP_DIR / "jmeter" / "jsm_agents.jmx"
JSM_JMX_CUSTOMERS = APP_DIR / "jmeter" / "jsm_customers.jmx"
JMETER_HOME = Path().home() / '.bzt' / 'jmeter-taurus'
WINDOWS = "Windows"
DEFAULT_HOSTNAMES = ['test_jira_instance.atlassian.com',
                     'test_confluence_instance.atlassian.com',
                     'test_bitbucket_instance.atlassian.com',
                     'test_jsm_instance.atlassian.com',
                     'test_crowd_instance.atlassian.com',
                     'test-bamboo.atlassian.com']
AGENTS = "agents"
CUSTOMERS = "customers"


class StartJMeter:

    def __init__(self):
        self.env_settings = dict()
        self.jmeter_properties = dict()
        parser = argparse.ArgumentParser(description='Edit yml config')
        parser.add_argument('--app', type=str, help='e.g. --app jira/confluence/bitbucket/jsm/bamboo')
        parser.add_argument('--type', type=str, help='jsm specific flag e.g. --type agents/customers')
        self.args = parser.parse_args()
        if not self.args.app:
            raise SystemExit('Application type is not specified. e.g. --app jira/confluence/bitbucket/jsm/bamboo')
        if self.args.app == JIRA:
            self.yml = JIRA_YML
            self.jmx = JIRA_JMX
        elif self.args.app == CONFLUENCE:
            self.yml = CONFLUENCE_YML
            self.jmx = CONFLUENCE_JMX
        elif self.args.app == BITBUCKET:
            self.yml = BITBUCKET_YML
            self.jmx = BITBUCKET_JMX
        elif self.args.app == CROWD:
            self.yml = CROWD_YML
            self.jmx = CROWD_JMX
        elif self.args.app == BAMBOO:
            self.yml = BAMBOO_YML
            self.jmx = BAMBOO_JMX
        elif self.args.app == JSM:
            if not self.args.type:
                raise SystemExit('JSM user type is not specified. e.g. --type agents/customers')

            self.yml = JSM_YML
            if self.args.type == AGENTS:
                self.jmx = JSM_JMX_AGENTS
            elif self.args.type == CUSTOMERS:
                self.jmx = JSM_JMX_CUSTOMERS
            else:
                raise SystemExit(f'JSM unsupported type: {self.args.type}. Valid types: {AGENTS}, {CUSTOMERS}')
        else:
            raise SystemExit("Application type {} is not supported. Valid values: {} {} {} {}".
                             format(self.args.app, JIRA, CONFLUENCE, BITBUCKET, JSM))

    @staticmethod
    def read_yml_file(file):
        with file.open(mode='r') as file:
            return yaml.load(file, Loader=yaml.FullLoader)

    @staticmethod
    def update_properties_file(content):
        with open(PROPERTIES, 'w') as file:
            file.writelines(content)

    @staticmethod
    def trim_string(text):
        for ch in ['{', '}', '$']:
            text = text.replace(ch, "")
        return text

    def get_settings(self):
        obj = self.read_yml_file(self.yml)
        self.env_settings = obj['settings']['env']
        hostname = self.env_settings['application_hostname']
        if hostname in DEFAULT_HOSTNAMES:
            raise SystemExit("ERROR: Check 'application_hostname' correctness in {}.yml file.\nCurrent value: {}.".
                             format(self.args.app, hostname))
        if self.args.app == JSM:
            self.jmeter_properties = obj['scenarios'][f'jmeter_{self.args.type}']['properties']
        else:
            self.jmeter_properties = obj['scenarios']['jmeter']['properties']
        settings = list()
        for setting, value in self.jmeter_properties.items():
            # if value referenced as variable
            if "$" in value:
                key = self.trim_string(value)
                v = self.env_settings[key]
            # if value set directly
            else:
                v = value
            if v is None:
                settings.append("{}=\n".format(setting))
            else:
                settings.append("{}={}\n".format(setting, v))
        return settings

    def print_settings(self, settings):
        print("Get JMeter settings from {} file:".format(self.yml))
        for setting in settings:
            print(setting.replace('\n', ''))

    def launch_jmeter_ui(self):
        jmeter_path = JMETER_HOME / self.env_settings['JMETER_VERSION'] / 'bin' / 'jmeter'
        command = [str(jmeter_path), "-p", str(PROPERTIES), "-t", str(self.jmx)]
        print("JMeter start command: {}".format(' '.join(command)))
        print("Working dir: {}".format(APP_DIR))
        shell = False
        if system() == WINDOWS:
            shell = True
        run(command, check=True, cwd=APP_DIR, shell=shell)

    def start(self):
        settings = self.get_settings()
        self.print_settings(settings)
        self.update_properties_file(settings)
        self.launch_jmeter_ui()


def main():
    sj = StartJMeter()
    sj.start()


if __name__ == "__main__":
    main()
