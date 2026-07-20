from locustio.common_utils import init_logger, jira_measure, run_as_specific_user  # noqa F401
from util.conf import JIRA_SETTINGS

logger = init_logger(app_type='jira')


@jira_measure("locust_customizations_scanner_status")
# WebSudo is a feature that enhances security by requiring administrators to re-authenticate before
# accessing administrative functions within Atlassian applications.
# do_websudo=True requires user administrative rights, otherwise requests fail.
#@run_as_specific_user(username='admin', password='admin', do_websudo=False)  # run as specific user
def app_specific_action(locust):
    config = JIRA_SETTINGS.customization_insights
    if not config.rest_path or not config.rest_assertion:
        raise ValueError(
            "Customization Insights 'rest_path' and 'rest_assertion' must be set "
            "under settings.env.customization_insights in app/jira.yml."
        )

    with locust.get(
        config.rest_path,
        headers={'Accept': 'application/json,text/plain,*/*'},
        catch_response=True,
    ) as r:
        content = r.content.decode('utf-8')
        if r.status_code != 200:
            message = f"Customization Scanner status endpoint returned {r.status_code}: {content}"
        elif config.rest_assertion not in content:
            message = f"'{config.rest_assertion}' was not found in {content}"
        else:
            return

        logger.error(message)
        r.failure(message)
