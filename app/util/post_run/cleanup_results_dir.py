import os
from util.project_paths import ENV_TAURUS_ARTIFACT_DIR

FILES_TO_REMOVE = ['jmeter.out',
                   'jmeter-bzt.properties',
                   'merged.json',
                   'merged.yml',
                   'PyTestExecutor.ldjson',
                   'system.properties',
                   'locust.out']

for file in FILES_TO_REMOVE:
    file_path = ENV_TAURUS_ARTIFACT_DIR / file
    if file_path.exists():
        try:
            os.remove(file_path)
            print(f'The {file} was removed successfully')
        except OSError as e:
            print(f'Warning: Deleting of the {file} failed! Error message: {file_path}: {e.strerror}')
