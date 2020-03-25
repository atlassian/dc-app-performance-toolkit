import os
from pathlib import Path
from shutil import rmtree


ENV_TAURUS_ARTIFACT_DIR = 'TAURUS_ARTIFACTS_DIR'
JMETER_JTL_FILE_NAME = 'kpi.jtl'

artifacts_dir = os.getenv(ENV_TAURUS_ARTIFACT_DIR)
if artifacts_dir is None:
    raise SystemExit(f'Error: env variable {ENV_TAURUS_ARTIFACT_DIR} is not set')

jmeter_home_path = Path().home() / '.bzt' / 'jmeter-taurus'

jmeter_jtl_file = f"{artifacts_dir}/{JMETER_JTL_FILE_NAME}"

if not os.path.exists(jmeter_jtl_file):
    if jmeter_home_path.exists():
        print(f'jmeter_post_check: removing {jmeter_home_path}')
        rmtree(str(jmeter_home_path))
    raise SystemExit(f'jmeter_post_check: ERROR - {jmeter_jtl_file} was not found. '
                     f'JMeter folder {jmeter_home_path} was removed for recovery '
                     f'and will be automatically downloaded on the next bzt run.')

print('jmeter_post_check: PASS')
