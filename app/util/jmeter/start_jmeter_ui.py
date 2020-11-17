import argparse
from pathlib import Path
from subprocess import run

import yaml

JIRA = "jira"
CONFLUENCE = "confluence"
BITBUCKET = "bitbucket"
JSM = "jsm"
APP_DIR = Path(__file__).resolve().parents[2]
PROPERTIES = APP_DIR / "util" / "jmeter" / "jmeter.properties"
JIRA_YML = APP_DIR / "jira.yml"
CONFLUENCE_YML = APP_DIR / "confluence.yml"
BITBUCKET_YML = APP_DIR / "bitbucket.yml"
JSM_YML = APP_DIR / "jsm.yml"
JIRA_JMX = APP_DIR / "jmeter" / "jira.jmx"
CONFLUENCE_JMX = APP_DIR / "jmeter" / "confluence.jmx"
BITBUCKET_JMX = APP_DIR / "jmeter" / "bitbucket.jmx"
JSM_JMX = APP_DIR / "jmeter" / "jsm.jmx"
JMETER_HOME = Path().home() / '.bzt' / 'jmeter-taurus'


class StartJMeter:

    def __init__(self):
        self.env_settings = dict()
        self.jmeter_properties = dict()
        parser = argparse.ArgumentParser(description='Edit yml config')
        parser.add_argument('--app', type=str, help='e.g. --app jira/confluence/bitbucket/jsm')
        self.args = parser.parse_args()
        if not self.args.app:
            raise SystemExit('Application type is not specified. e.g. --app jira/confluence/bitbucket/jsm')
        if self.args.app == JIRA:
            self.yml = JIRA_YML
            self.jmx = JIRA_JMX
        elif self.args.app == CONFLUENCE:
            self.yml = CONFLUENCE_YML
            self.jmx = CONFLUENCE_JMX
        elif self.args.app == BITBUCKET:
            self.yml = BITBUCKET_YML
            self.jmx = BITBUCKET_JMX
        elif self.args.app == JSM:
            self.yml = JSM_YML
            self.jmx = JSM_JMX
        else:
            raise SystemExit(f"Application type {self.args.app} is not supported. "
                             f"Valid values: {JIRA} {CONFLUENCE} {BITBUCKET} {JSM}")

    @staticmethod
    def read_yml_file(file):
        with file.open(mode='r') as file:
            return yaml.load(file, Loader=yaml.FullLoader)

    @staticmethod
    def update_properties_file(content):
        with open(PROPERTIES, 'w') as f:
            f.writelines(content)

    @staticmethod
    def trim_string(text):
        for ch in ['{', '}', '$']:
            text = text.replace(ch, "")
        return text

    def get_settings(self):
        obj = self.read_yml_file(self.yml)
        self.env_settings = obj['settings']['env']
        self.jmeter_properties = obj['scenarios']['jmeter']['properties']
        settings = list()
        for setting, value in self.jmeter_properties.items():
            # if value referenced as variable
            if "$" in value:
                key = self.trim_string(value)
                v = self.env_settings[f'{key}']
            # if value set directly
            else:
                v = value
            if v is None:
                settings.append(f"{setting}=\n")
            else:
                settings.append(f"{setting}={v}\n")
        return settings

    def print_settings(self, settings):
        print(f"Get JMeter settings from {self.yml} file:")
        for setting in settings:
            print(setting, end="")

    def launch_jmeter_ui(self):
        jmeter_path = JMETER_HOME / self.env_settings['JMETER_VERSION'] / 'bin' / 'jmeter'
        command = [f"{jmeter_path}", "-p", f"{PROPERTIES}", "-t", f"{self.jmx}"]
        print(f"JMeter start command: {' '.join(command)}")
        print(f"Working dir: {APP_DIR}")
        run(command, check=True, cwd=APP_DIR)

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
