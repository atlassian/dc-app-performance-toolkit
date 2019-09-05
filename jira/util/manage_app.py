import sys
from pathlib import Path
import yaml
from optparse import OptionParser

"""
This util can be used for plugin management. In the following way it may be used:
python manage_app.py [--disable] || [--enable] --application-key $application_key
This command can be add to jira.yml as part of services[module][prepare]
"""

# Work around import issue
import os

sys.path.insert(0, os.path.dirname(os.getcwd()))
print("System path: ", sys.path)

from jira.selenium_ui.api import ApiJira


def application_url():
    with open(Path(__file__).parents[1] / "jira.yml", 'r') as file:
        jira_yaml = yaml.load(file, Loader=yaml.FullLoader)
        protocol = jira_yaml['settings']['env']['application_protocol']
        dom_name = jira_yaml['settings']['env']['application-url']
        app_url = f"{protocol}://{dom_name}"
        return app_url


application_url = application_url()
jira_api = ApiJira(application_url)


def parse_cli():
    parser = OptionParser(usage="Usage: python manage_app.py [args]")
    parser.add_option("-d", "--disable",
        help="Disable Jira plugin by application key",
        dest="disable", action="store_true")
    parser.add_option("-e", "--enable",
        help="Enable Jira plugin by application key",
        dest="enable", action="store_true")

    parser.add_option("-k", "--application-key",
        help="Jira application key",
        dest="key", type="string")

    (opts, args) = parser.parse_args()
    return opts, args


def set_application_mode(app_key, enable=False):
    app_info = jira_api.get_app_info(app_key)
    if enable:
        if not app_info['enabled']:
            app_info['enabled'] = True
            jira_api.update_app(app_key, app_info)
    if not enable:
        if app_info['enabled']:
            app_info['enabled'] = False
            jira_api.update_app(app_key, app_info)


def main():
    (opts, args) = parse_cli()
    if opts.disable and opts.key:
        application_key = opts.key
        print('Started disabling application {}'.format(application_key))
        set_application_mode(application_key, enable=False)
        print('Application {} disabled'.format(application_key))

    elif opts.enable and opts.key:
        application_key = opts.key
        print('Started enabling application {}'.format(application_key))
        set_application_mode(application_key, enable=True)
        print('Application {} enabled'.format(application_key))


if __name__ == "__main__":
    main()
