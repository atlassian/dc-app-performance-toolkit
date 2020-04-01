from pathlib import Path
import os

ENV_TAURUS_ARTIFACT_DIR = 'TAURUS_ARTIFACTS_DIR'
FILES_TO_REMOVE = ['jmeter.out',
                   'jmeter-bzt.properties',
                   'merged.json',
                   'merged.yml',
                   'PyTestExecutor.ldjson',
                   'system.properties']

if ENV_TAURUS_ARTIFACT_DIR in os.environ:
    artifacts_dir = os.environ.get(ENV_TAURUS_ARTIFACT_DIR)
else:
    raise SystemExit(f'Error: env variable {ENV_TAURUS_ARTIFACT_DIR} is not set')

for file in FILES_TO_REMOVE:
    file_path = Path(f'{artifacts_dir}/{file}')
    try:
        os.remove(file_path)
        print(f'The {file} was removed successfully')
    except OSError as e:
        print(f'Deleting of the {file} failed!\n'
              f'Error: {file_path}: {e.strerror}')
