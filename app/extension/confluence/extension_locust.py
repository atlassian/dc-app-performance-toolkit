from locustio.common_utils import init_logger, confluence_measure, run_as_specific_user  # noqa F401
from util.conf import CONFLUENCE_SETTINGS

logger = init_logger(app_type='confluence')


@confluence_measure("locust_customization_insights")
# WebSudo is a feature that enhances security by requiring administrators to re-authenticate before
# accessing administrative functions within Atlassian applications.
# do_websudo=True requires user administrative rights, otherwise requests fail.
#@run_as_specific_user(username='admin', password='admin', do_websudo=False)  # run as specific user
def app_specific_action(locust):
    config = CONFLUENCE_SETTINGS.customization_insights
    if not config.rest_path or not config.rest_assertion:
        raise ValueError(
            "Customization Insights 'rest_path' and 'rest_assertion' must be set "
            "under settings.env.customization_insights in app/confluence.yml."
        )

    r = locust.get(config.rest_path, headers={'Accept': 'application/json,text/plain,*/*'}, catch_response=True)
    content = r.content.decode('utf-8')
    if config.rest_assertion not in content:
        logger.error(f"'{config.rest_assertion}' was not found in {content}")
    assert config.rest_assertion in content
