import re
from locustio.common_utils import init_logger

logger = init_logger(app_type='confluence')


def custom_action(locust):
    r = locust.client.get('/plugin/report')  # navigate to page

    content = r.content.decode('utf-8')  # parse page content
    token_pattern_example = '"token":"(.+?)"'
    id_pattern_example = '"id":"(.+?)"'
    token = re.findall(token_pattern_example, content)  # parse variables from response using regexp
    id = re.findall(id_pattern_example, content)
    logger.locust_info(f'token: {token}, id: {id}')  # logger for debug
    assert 'assertion string' in content  # assertion after GET request

    body = {"id": id, "token": token}  # include parsed variables to POST body
    headers = {'content-type': 'application/json'}
    r = locust.client.post('/plugin/post/endpoint', body, headers)  # send some POST request
    content = r.content.decode('utf-8')

    assert 'assertion string after successful post request' in content  # assertion after POST request
