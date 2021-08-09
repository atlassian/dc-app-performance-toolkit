import requests
from packaging import version

from util.conf import TOOLKIT_VERSION, UNSUPPORTED_VERSION


CONF_URL = "https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/conf.py"
VERSION_STR = "TOOLKIT_VERSION"

r = requests.get(CONF_URL)

if not r.ok:
    print(f"Warning: DCAPT check for updates failed.\nURL: {r.url}. Status code: {r.status_code}. Reason: {r.reason}")
    exit(0)

conf = r.text.splitlines()
version_line = next((line for line in conf if VERSION_STR in line))
latest_version_str = version_line.split('=')[1].replace("'", "").replace('"', "").strip()

latest_version = version.parse(latest_version_str)
current_version = version.parse(TOOLKIT_VERSION)
unsupported_version = version.parse(UNSUPPORTED_VERSION)

if current_version <= unsupported_version:
    raise SystemExit(f"DCAPT version {current_version} is no longer supported. "
                     f"Consider an upgrade to the latest version: {latest_version}")
elif current_version < latest_version:
    print(f"Warning: DCAPT version {TOOLKIT_VERSION} is outdated. "
          f"Consider upgrade to the latest version: {latest_version}.")
elif current_version == latest_version:
    print(f"Info: DCAPT version {TOOLKIT_VERSION} is latest.")
else:
    print(f"Info: DCAPT version {TOOLKIT_VERSION} is ahead of the latest production version: {latest_version}.")
