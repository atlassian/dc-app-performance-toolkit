import requests
import json
from fixtures import session
import os
import random
import pathlib


HOSTNAME = os.environ.get('application_hostname')

CURRENT_PATH = pathlib.Path().absolute()
delete_diagram_file_path = CURRENT_PATH / "deleteCreatedObjects"

class TestDelete:
    def test_delete(self, session):
        with open(delete_diagram_file_path) as f:
            for line in f:
                print("Line:" + line);
                deleteLine = line.strip();
                print(deleteLine)
                diagrams_response = session.delete(deleteLine)
                assert diagrams_response.status_code == 200
                print("OK")
        f.close()