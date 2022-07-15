import os

import requests
from requests.auth import HTTPBasicAuth

USR = os.environ.get('JIRA_USERNAME')
PWD = os.environ.get('JIRA_PASSWORD')

WEB_HOOK = os.environ.get('SLACK_HOOK')
JIRA_API = os.environ.get('JIRA_API_URL')

# Issues states in Jira
OPEN = '1'
IN_PROGRESS = '3'
REOPENED = '4'
RESOLVED = '5'
CLOSED = '6'


def get_all_issues_for_test_case(test_case):
    jira_query = JIRA_API + "jql=(testname=" + test_case + ")&fields=key,status"
    return requests.get(url=jira_query,
                        auth=HTTPBasicAuth(USR, PWD))


def get_not_closed_issues_for_test_case(test_case):
    jira_query = JIRA_API + "jql=(type!=\"Test\"+and+testname=" + test_case \
                 + ")+and+(status=" + OPEN \
                 + "+or+status=" + IN_PROGRESS \
                 + "+or+status=" + REOPENED \
                 + "+or+status=" + RESOLVED \
                 + ")&fields=key,status,labels"
    return requests.get(url=jira_query,
                        auth=HTTPBasicAuth(USR, PWD))


def send_slack_message(message):
    response = requests.post(WEB_HOOK, None, message)
    print(response)


def get_job_result():
    return requests.get(url=os.environ.get('BUILD_URL') + "api/xml")
