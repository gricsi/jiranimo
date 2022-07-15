import os
import sys
import time

from models.platform import Platform
from models.test_case import TestCase
from models.test_run import TestRun
from parsers.jenkins_junit_report_parser import get_all_test_cases_from_xml_reports, get_test_run_details, \
    get_duration_from_jenkins_job
from parsers.jira_response_parser import parse_response
from requests_repository import get_not_closed_issues_for_test_case, send_slack_message, get_job_result
from slack_message import SlackMessage

test_results_folder_path = sys.argv[1]
platform = sys.argv[2]  # i.e. android, ios, web
job_name = sys.argv[3]
job_url = sys.argv[4]

test_cases = []
test_run = TestRun
failed_test_cases = []
successful_test_cases = []
slack_message = SlackMessage()
slack_channel = os.environ.get('SLACK_CHANNEL')
url = ''

test_cases = get_all_test_cases_from_xml_reports(test_results_folder_path, platform)
test_run = get_test_run_details(test_results_folder_path, job_name, job_url, platform)

# Parse test results files and generate list of TestCase objects
if platform == Platform.android:
    url = job_url + "testReport/junit/"
    if slack_channel == "":
        slack_channel = "#qa-reporting-android"
elif platform == Platform.ios:
    url = job_url + "testReport/(root)/"
    if slack_channel == "":
        slack_channel = "#qa-reporting-ios"
elif platform == Platform.web:
    url = job_url + "testReport/junit/(root)/"
    if slack_channel == "":
        slack_channel = "#qa-reporting-web"
else:
    # Handle case when nothing provided
    print

# Populate each test cases with
for tc in test_cases:  # type: TestCase()

    # Workaround for parametrised tests
    tc_name = str(tc.name).replace("()", "").split("[")

    if not tc.is_successful:

        # Fetch jira tickets for test case name
        jira_issues_response = get_not_closed_issues_for_test_case(tc_name[0])  # Take 1st value from array

        jira_issues = parse_response(jira_issues_response.text)
        if jira_issues.__len__() > 0:
            # Jira tickets found - existing bug (specific case - old closed jira ticket TODO - handle it)
            for issue in jira_issues:
                if issue.is_test_issue:
                    slack_message.add_test_issue(tc)
                elif issue.is_flaky_test_issue:
                    slack_message.add_flaky_test_issue(tc)
                else:
                    slack_message.add_bug(tc)
            tc.add_jira_issues(jira_issues)
        else:
            # Jira tickets not found - regression
            slack_message.add_regression(tc)

job_result = get_job_result()
start_milli_time = get_duration_from_jenkins_job(job_result.content)
current_milli_time = int(round(time.time() * 1000))

minutes = int((current_milli_time - start_milli_time) / 60000)

# Build report for slack
report = SlackMessage.build_report(slack_message, test_run, slack_channel, minutes, url)

# Send test report
send_slack_message(report)
