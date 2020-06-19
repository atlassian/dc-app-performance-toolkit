import re
from locustio.common_utils import init_logger, confluence_measure

logger = init_logger(app_type='confluence')


@confluence_measure
def app_specific_action(locust):

    r = locust.client.get('/plugin/report')  # navigate to page

    content = r.content.decode('utf-8')  # parse page content
    token_pattern_example = '"token":"(.+?)"'
    id_pattern_example = '"id":"(.+?)"'
    token = re.findall(token_pattern_example, content)  # parse variables from response using regexp
    id = re.findall(id_pattern_example, content)
    logger.locust_info(f'token: {token}, id: {id}')  # logger for debug when verbose is true in confluence.yml file
    if 'assertion string' not in content:
        logger.error(f"'assertion string' was not found in {content}")
    assert 'assertion string' in content  # assertion after GET request

    body = {"id": id, "token": token}  # include parsed variables to POST body
    headers = {'content-type': 'application/json'}
    r = locust.client.post('/plugin/post/endpoint', body, headers)  # send some POST request
    content = r.content.decode('utf-8')
    if 'assertion string after successful post request' not in content:
        logger.error(f"'assertion string after successful post request' was not found in {content}")
    assert 'assertion string after successful post request' in content  # assertion after POST request
