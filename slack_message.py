# !/usr/bin/env python 3
from __future__ import with_statement

import contextlib
import os

from models.test_case import TestCase

try:
    from urllib.parse import urlencode

except ImportError:
    from urllib import urlencode
try:
    from urllib.request import urlopen

except ImportError:
    from urllib2 import urlopen


def make_tiny(url):
    request_url = ('http://tinyurl.com/api-create.php?' + urlencode({'url': url}))
    with contextlib.closing(urlopen(request_url)) as response:
        return response.read().decode('utf-8 ')


JIRA_LINK = os.environ.get('JIRA_LINK')
green = "#228B22"
orange = "#ffa500"
light_orange = "#ffe4b2"
red = "#B22222"
grey = "#808080"
android_logo = ":android_logo:"
ios_logo = ":ios_logo:"
web_logo = ":web_logo:"
message_logo = ''


def name_time_link(test_case, url):
    short = make_tiny(url + test_case.link)

    text_link = "<{0}|{1}>".format(short, test_case.time)

    if test_case.age == '':
        return " - {0}, {1}".format(test_case.slack_report_name, text_link)
    else:
        return " - {0} [{1}], {2}".format(test_case.slack_report_name, str(test_case.age), text_link)


def method_name(test_list):
    name_and_time = ""
    sorted(test_list)
    for key, value in test_list.items():
        name_and_time += "<{0}|{1}>\n{2}".format(JIRA_LINK + key, key, value)
        name_and_time += "\n"
    return name_and_time


class SlackMessage:

    def __init__(self):
        pass

    regressions = []  # type: [TestCase()]
    test_issues = []  # type: [TestCase()]
    flaky_test_issues = []  # type: [TestCase()]
    bugs = []  # type: [TestCase()]
    successful = []  # type: [TestCase()]

    def add_regression(self, test_case):
        self.regressions.append(test_case)

    def add_test_issue(self, test_case):
        self.test_issues.append(test_case)

    def add_flaky_test_issue(self, test_case):
        self.flaky_test_issues.append(test_case)

    def add_bug(self, test_case):
        self.bugs.append(test_case)

    def add_successful(self, test_case):
        self.successful.append(test_case)

    def write_json_regressions(self, url):
        self.regressions.sort(key=lambda x: (x.stacktrace, x.slack_report_name))

        if self.regressions.__len__() > 0:
            regression_fields = []
            group_by_stacktrace = {}

            for regression in self.regressions:
                if regression.stacktrace in group_by_stacktrace:
                    text = group_by_stacktrace[regression.stacktrace] + "\n" + name_time_link(regression, url)
                    group_by_stacktrace.update({regression.stacktrace: text})
                else:
                    text = name_time_link(regression, url)
                    group_by_stacktrace.update({regression.stacktrace: text})

            sorted(group_by_stacktrace)

            for key, value in group_by_stacktrace.items():
                regression_fields.append({
                    "value": "`{0}`\n{1}".format(key, value)
                })

            return {"color": grey,
                    "title": "Regressions: " + str(self.regressions.__len__()),
                    "fields": regression_fields}

    def write_json_bugs(self, url):
        self.bugs.sort(key=lambda x: x.slack_report_name)

        if self.bugs.__len__() > 0:
            bug_fields = []
            existing_group_by_ticket_id = {}

            for previously_failed_cases in self.bugs:
                name_and_time = name_time_link(previously_failed_cases, url)
                if len(previously_failed_cases.jira_issues) > 0:
                    for jira_issues in previously_failed_cases.get_jira_issues():
                        for issue in jira_issues:
                            if not issue.is_test_issue and not issue.is_flaky_test_issue:
                                if issue.key in existing_group_by_ticket_id:
                                    # filter out the duplication when one testName appears in multiple tickets
                                    if name_and_time not in existing_group_by_ticket_id[issue.key]:
                                        text = existing_group_by_ticket_id[issue.key] + "\n" + name_and_time
                                        existing_group_by_ticket_id.update({issue.key: text})
                                    else:
                                        "do nothing it's in the list already "
                                else:
                                    text = name_and_time
                                    existing_group_by_ticket_id.update({issue.key: text})

            bug_fields.append({
                "value": method_name(existing_group_by_ticket_id)
            })

            return {"color": red,
                    "title": "Bugs: " + str(self.bugs.__len__()),
                    "fields": bug_fields}

    def write_json_test_issues(self, url):
        self.test_issues.sort(key=lambda x: x.slack_report_name)

        if self.test_issues.__len__() > 0:
            test_fields = []
            existing_group_by_ticket_id = {}

            for previously_failed_cases in self.test_issues:
                name_and_time = name_time_link(previously_failed_cases, url)
                if len(previously_failed_cases.jira_issues) > 0:
                    for jira_issues in previously_failed_cases.get_jira_issues():
                        for issue in jira_issues:
                            if issue.is_test_issue:
                                if issue.key in existing_group_by_ticket_id:
                                    # filter out the duplication when one testName appears in multiple tickets
                                    if name_and_time not in existing_group_by_ticket_id[issue.key]:
                                        text = existing_group_by_ticket_id[issue.key] + "\n" + name_and_time
                                        existing_group_by_ticket_id.update({issue.key: text})
                                    else:
                                        "do nothing it's in the list already "
                                else:
                                    text = name_and_time
                                    existing_group_by_ticket_id.update({issue.key: text})

            test_fields.append({
                "value": method_name(existing_group_by_ticket_id)
            })

            return {"color": orange,
                    "title": "Test issues: " + str(self.test_issues.__len__()),
                    "fields": test_fields}

    def write_json_flaky_test_issues(self, url):
        self.flaky_test_issues.sort(key=lambda x: x.slack_report_name)

        if self.flaky_test_issues.__len__() > 0:
            flaky_test_fields = []
            existing_group_by_ticket_id = {}

            for previously_failed_cases in self.flaky_test_issues:
                name_and_time = name_time_link(previously_failed_cases, url)
                if len(previously_failed_cases.jira_issues) > 0:
                    for jira_issues in previously_failed_cases.get_jira_issues():
                        for issue in jira_issues:
                            if issue.is_flaky_test_issue:
                                if issue.key in existing_group_by_ticket_id:
                                    # filter out the duplication when one testName appears in multiple tickets
                                    if name_and_time not in existing_group_by_ticket_id[issue.key]:
                                        text = existing_group_by_ticket_id[issue.key] + "\n" + name_and_time
                                        existing_group_by_ticket_id.update({issue.key: text})
                                    else:
                                        "do nothing it's in the list already "
                                else:
                                    text = name_and_time
                                    existing_group_by_ticket_id.update({issue.key: text})

            flaky_test_fields.append({
                "value": method_name(existing_group_by_ticket_id)
            })

            return {"color": light_orange,
                    "title": "Flaky test issues: " + str(self.flaky_test_issues.__len__()),
                    "fields": flaky_test_fields}

    def build_report(self, test_run, slack_channel, minutes, url):

        if test_run.platform == "android":
            message_logo = android_logo
        elif test_run.platform == "ios":
            message_logo = ios_logo
        else:
            message_logo = web_logo

        footer_text = "Environment - %s | Branch - %s" % \
                      (os.getenv('ENVIRONMENT', os.environ.get('UITESTS_ENVIRONMENT')), os.environ.get('FROM'))

        if self.regressions.__len__() == 0 \
                and self.bugs.__len__() == 0 \
                and self.flaky_test_issues.__len__() == 0 \
                and self.test_issues.__len__() == 0 \
                and test_run.tests != "0":
            data = {"attachments": [{"color": green,
                                     "title": "Successful test result",
                                     "footer": footer_text}]}

        elif test_run.tests == "0":
            data = {"attachments": [{"color": red,
                                     "title": "Test run failed - no test result files to parse.",
                                     "footer": footer_text}]}
        else:
            data = {"attachments": []}
            attachments = data["attachments"]

            regressions = self.write_json_regressions(url)
            attachments.append(regressions)

            bugs = self.write_json_bugs(url)
            attachments.append(bugs)

            test_issues = self.write_json_test_issues(url)
            attachments.append(test_issues)

            flaky_test_issues = self.write_json_flaky_test_issues(url)
            attachments.append(flaky_test_issues)

            attachments.append({"footer": footer_text})

        data["text"] = "*Number of tests: {0}, failures: {1}, skipped: {2}. Took {3} minutes.* (<{4}|Open job>)".format(
            test_run.tests, test_run.failures, test_run.skipped, str(minutes), test_run.url)

        data["channel"] = slack_channel
        data["username"] = test_run.name
        data["icon_emoji"] = message_logo

        return data
