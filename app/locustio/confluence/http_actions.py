import itertools
import inspect
import logging
import random
import re

from locustio.common_utils import confluence_measure
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

    params = Login
    login_body = params.login_body
    login_body['os_username'] = username
    login_body['os_password'] = password
    locust.client.post('/dologin.action', login_body, TEXT_HEADERS, catch_response=True)
    r = locust.client.get('/', catch_response=True)
    locust.logger.info(r.content.decode('utf-8'))


