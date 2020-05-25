import itertools
import inspect
import logging
import random
import re

from locustio.common_utils import confluence_measure, fetch_by_re
from locustio.confluence.requests_params import confluence_datasets, Login
from locustio.jira.requests_params import TEXT_HEADERS, ADMIN_HEADERS, NO_TOKEN_HEADERS


counter = itertools.count()
confluence_dataset = confluence_datasets()


@confluence_measure
def login_and_view_dashboard(locust):
    func_name = inspect.stack()[0][3]
    locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
    user = random.choice(confluence_dataset["users"])
    username = user[0]
    password = user[1]

    params = Login()
    login_body = params.login_body
    login_body['os_username'] = username
    login_body['os_password'] = password
    locust.client.post('/dologin.action', login_body, TEXT_HEADERS, catch_response=True)
    r = locust.client.get('/', catch_response=True)
    content = r.content.decode('utf-8')
    assert 'Log Out' in content, f'Login with {username}, {password} failed.'
    locust.logger.info(f'User {username} is successfully logged in')
    keyboard_hash = fetch_by_re(params.keyboard_hash_re, content)
    static_resource_url = fetch_by_re(params.static_resource_url_re, content)
    version_number = fetch_by_re(params.version_number_re, content)
    build_number = fetch_by_re(params.build_number_re, content)
    locust.client.post('/rest/webResources/1.0/resources', params.body["1"],
                       TEXT_HEADERS, catch_response=True)
    locust.client.get('/rest/mywork/latest/status/notification/count', catch_response=True)





