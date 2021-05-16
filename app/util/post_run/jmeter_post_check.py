import os
from pathlib import Path
from shutil import rmtree
from util.project_paths import ENV_TAURUS_ARTIFACT_DIR


JMETER_JTL_FILE_NAME = 'kpi.jtl'

jmeter_home_path = Path().home() / '.bzt' / 'jmeter-taurus'
jmeter_jtl_file = ENV_TAURUS_ARTIFACT_DIR / JMETER_JTL_FILE_NAME

if not os.path.exists(jmeter_jtl_file):
    if jmeter_home_path.exists():
        print(f'jmeter_post_check: removing {jmeter_home_path}')
        rmtree(str(jmeter_home_path))
    raise SystemExit(f'jmeter_post_check: ERROR - {jmeter_jtl_file} was not found. '
                     f'JMeter folder {jmeter_home_path} was removed for recovery '
                     f'and will be automatically downloaded on the next bzt run.')

print('jmeter_post_check: PASS')
