from util.conf import JIRA_SETTINGS
import time

scenarios = JIRA_SETTINGS.scenarios
total_actions_per_hr_jira = JIRA_SETTINGS.scenarios['locust']['properties']['total_actions_per_hr']


action_time_jira_ms = (1000 * 3600) / total_actions_per_hr_jira / JIRA_SETTINGS.concurrency


print(action_time_jira_ms)

start = time.time()
print(start)
time.sleep(2)
finish = time.time() - start
print(finish)
time.sleep(-2)