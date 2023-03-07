import http
import json
import re
from pprint import pprint

import filelock
import pytest
import requests

from conf import CONFLUENCE_SETTINGS
from selenium_ui.confluence.pages.selectors import UrlManager


@pytest.fixture(scope="module", autouse=True)
def zdu_nodes_info(confluence_webdriver, tmp_path_factory):
    if not CONFLUENCE_SETTINGS.zdu:
        return

    def get_cluster_info() -> dict:
        resp = requests.get(
            f'{CONFLUENCE_SETTINGS.protocol}://{CONFLUENCE_SETTINGS.hostname}/rest/zdu/cluster',
            auth=(CONFLUENCE_SETTINGS.admin_login, CONFLUENCE_SETTINGS.admin_password)
        )
        if resp.status_code != http.HTTPStatus.OK:
            raise SystemExit("Cannot get cluster info. Aborting!")
        cluster_info = resp.json()
        return {node["id"]: node["ipAddress"] for node in cluster_info["nodes"]}

    root_tmp_dir = tmp_path_factory.getbasetemp().parent
    fn = root_tmp_dir / "nodes_info.json"
    with filelock.FileLock(str(fn) + ".lock"):
        if fn.is_file():
            nodes_info = json.loads(fn.read_text())
        else:
            nodes_info = get_cluster_info()
            fn.write_text(json.dumps(nodes_info))
    pprint(f"Nodes map: {nodes_info}")

    r = requests.get(UrlManager().login_url())
    if r.status_code != http.HTTPStatus.OK:
        raise SystemExit("Couldn't retrieve node id form login page. Aborting!")
    r = re.search(r"node:.(.*)\)", r.text)
    if not r:
        raise SystemExit("Couldn't retrieve node id form login page. Aborting!")
    node_id = r.group(1)
    confluence_webdriver.node_ip = nodes_info[node_id]
