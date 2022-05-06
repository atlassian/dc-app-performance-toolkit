import re
from locustio.common_utils import init_logger, jira_measure, run_as_specific_user  # noqa F401

logger = init_logger(app_type='jira')
issue_key="PROJT-83"
case_id="500J000000VTOJVIA5"

@jira_measure("locust_app_specific_action")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user

def app_specific_action(locust):
    """GET ATTACHMENTS"""
    r = locust.get(f'/rest/zagile-sf/1.0/attachment/{issue_key}?entityId={case_id}', catch_response=True)  # call app-specific GET endpoint
    content = r.content.decode('utf-8')   # decode response content

    token_pattern_example = '"token":"(.+?)"'
    id_pattern_example = '"id":"(.+?)"'
    token = re.findall(token_pattern_example, content)  # get TOKEN from response using regexp
    id = re.findall(id_pattern_example, content)    # get ID from response using regexp

    logger.locust_info(f'token: {token}, id: {id}')  # log info for debug when verbose is true in jira.yml file
    if 'attachments' not in content:
        logger.error(f"'assertion string' was not found in {content}")
    assert 'attachments' in content  # assert specific string in response content


    """GET COMMENT"""
    r = locust.get(f'/rest/zagile-sf/1.0/comment/{case_id}?limit=20&offset=0',
                   catch_response=True)
    content = r.content.decode('utf-8')

    token_pattern_example = '"token":"(.+?)"'
    id_pattern_example = '"id":"(.+?)"'
    token = re.findall(token_pattern_example, content)
    id = re.findall(id_pattern_example, content)

    logger.locust_info(f'token: {token}, id: {id}')
    if 'comments' not in content:
        logger.error(f"'comments do not exist in {content}")
    assert 'comments' in content


    """GET FEEDS"""
    r = locust.get(f'/rest/zagile-sf/1.0/{issue_key}/feed/{case_id}?pageSize=20',
                   catch_response=True)
    content = r.content.decode('utf-8')

    token_pattern_example = '"token":"(.+?)"'
    id_pattern_example = '"id":"(.+?)"'
    token = re.findall(token_pattern_example, content)
    id = re.findall(id_pattern_example, content)

    logger.locust_info(f'token: {token}, id: {id}')
    if 'feeds' not in content:
        logger.error(f"'feeds do not exist in {content}")
    assert 'feeds' in content


    """GET EMAILS"""
    r = locust.get(f'/rest/zagile-sf/1.0/{issue_key}/email/{case_id}?limit=20&offset=0',
                   catch_response=True)
    content = r.content.decode('utf-8')

    token_pattern_example = '"token":"(.+?)"'
    id_pattern_example = '"id":"(.+?)"'
    token = re.findall(token_pattern_example, content)
    id = re.findall(id_pattern_example, content)

    logger.locust_info(f'token: {token}, id: {id}')
    if 'emails' not in content:
        logger.error(f"'feeds do not exist in {content}")
    assert 'emails' in content





    """POST IMPORT"""
    pyload = {"entityId": "500J000000VTNhkIAH", "filename": "image (1).png", "contentType": "image/png", "attachmentObjName": "Attachment", "attachmentId": "00PJ0000009enmLMAQ"}
    r = locust.post(
        f'/rest/zagile-sf/1.0/attachment/{issue_key}/import?token=Zr%2BosnUZUJuURjpRsEkTUhq2%2B4ycoI8546O1sNlhWmc%3D',
        json=pyload, headers={'content-type': 'application/json', 'Accept': 'application/json', 'Content-Length': '155'},
        catch_response=True)  # call app-specific POST endpoint

    assert r.status_code is 200, "import string after successful POST request' was not found "  # assertion after POST request


    """POST DOWNLOAD"""
    r = locust.post(
        f'/plugins/servlet/downloadSalesforceAttachment?attachmentId=00PJ0000009eqg9MAA&issueKey={issue_key}&entityId=500J000000VTNhkIAH&attachmentName=bar.jpg&token=8u3Bgg%2FyBFtHMt2uFFO4Fw5s9QEtP%2BGZWymYM2M2qDM%3D&sObjName=Attachment&contentType=image/jpeg',
        headers={'content-type': 'application/json', 'Accept': 'application/json', 'X-Atlassian-Token': 'no-check'},
        catch_response=True)

    assert r.status_code is 200, "download string after successful POST request' was not found "
