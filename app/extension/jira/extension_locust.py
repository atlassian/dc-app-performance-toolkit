import re
from locustio.common_utils import logger


def custom_action(locust):
    r = locust.client.get(f'/plugin/report')

    content = r.content.decode('utf-8')
    token_pattern_example = '"token":"(.+?)"'
    id_pattern_example = '"id":"(\d+?)"'
    token = re.findall(token_pattern_example, content)
    id = re.findall(id_pattern_example, content)
    logger.debug(f'token: {token}, id: {id}')  # logger for debug
    assert 'assertion string' in content

    body = {"id": id, "token": {token}}
    headers = {'content-type': 'application/json'}
    r = locust.client.post('/plugin/post/endpoint', body, headers)
    content = r.content.decode('utf-8')

    assert 'assertion string after successful post request' in content

