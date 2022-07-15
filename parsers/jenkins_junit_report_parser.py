import os
import re
from xml.dom import minidom

from models.platform import Platform
from models.test_case import TestCase
from models.test_run import TestRun

# XML junit report attributes
XML = ".xml"
TEST_CASE = 'testcase'
FAILURE = 'failure'
NAME_ATTRIBUTE = 'name'
CLASS_NAME_ATTRIBUTE = 'classname'
TIME_ATTRIBUTE = 'time'

TEST_SUITE = 'testsuite'
TESTS = 'tests'
FAILURES = 'failures'
SKIPPED = 'skipped'
NO_TESTS_FOUND = "no tests found"

all_test_cases = []
error_screen_type_list = ["Screen.", "Widget.", "State.", "TimelineHeader", "FilterMenu", "TimelineInsight",
                          "TimelineTransaction"]


# Parses each file inside folder and returns test case names per file
def get_test_cases_per_file(file_path, platform):
    test_cases_per_file = []

    print(file_path)
    if file_path.lower().endswith(XML):
        xml_doc = minidom.parse(file_path)
        # Get all test case names
        test_cases = xml_doc.getElementsByTagName(TEST_CASE)

        # Iterate through test cases and add its attributes: name, time, pass/fail
        for tc in test_cases:

            name = tc.attributes[NAME_ATTRIBUTE].value
            class_name = tc.attributes[CLASS_NAME_ATTRIBUTE].value

            if class_name == NO_TESTS_FOUND:
                continue

            try:
                time_with_milliseconds = tc.attributes[TIME_ATTRIBUTE].value
            except KeyError:
                time_with_milliseconds = "0.0"

            time = time_with_milliseconds.split(".")
            failed_test_case = tc.getElementsByTagName(FAILURE)
            stacktrace_short = 'Cannot escape short stacktrace'
            if failed_test_case.__len__() > 0:

                if platform == Platform.ios:
                    if failed_test_case[0].attributes.length != 0:
                        stacktrace = failed_test_case[0].attributes["message"].value  # iOS
                        temp = ''.join(reversed(stacktrace)).split("/")[0]
                        temp = ''.join(reversed(temp))
                        if re.search(r'.*.swift', temp):
                            stacktrace_short = "{0}:{1}".format(re.search(r'.*.swift', temp).group(),
                                                                re.search(r'[0-9]+\)', temp).group().replace(")", ""))
                        elif re.search(r'.*.Numbrs crashed.*\(', stacktrace):
                            stacktrace_short = re.search(r'Numbrs crashed.* ', stacktrace).group()
                        else:
                            stacktrace_short = failed_test_case[0].firstChild.nodeValue
                if platform == Platform.android:
                    # Android xml
                    stacktrace = failed_test_case[0].firstChild.nodeValue
                    # Parse error stack trace for the first [Foo]Screen related line
                    for line in stacktrace.split("\n"):
                        for error in error_screen_type_list:
                            if error in line:
                                if line.partition(error).__len__() == 3:
                                    stacktrace_short = line.partition(error)[2]
                                    break

                if platform == Platform.web:
                    if failed_test_case[0].attributes.length != 0:
                        stacktrace = failed_test_case[0].attributes["message"].value
                        if "data-test-selector" in stacktrace:
                            stacktrace_short = "{0}".format(re.search(r'\[.*\]', stacktrace).group())
                        else:
                            for node in failed_test_case[0].childNodes:
                                if re.search(r'\/(?:.(?!\/))+$', node.nodeValue):
                                    stacktrace_short = "{0}".format(
                                        re.search(r'\/(?:.(?!\/))+$', node.nodeValue).group().replace("/", "")
                                            .replace(")", ""))

                test_case_object = TestCase(name, class_name, time[0] + "s", '', False, stacktrace_short)
                test_cases_per_file.append(test_case_object)
            else:
                test_case_object = TestCase(name, class_name, time[0] + "s", '', True, '')
                test_cases_per_file.append(test_case_object)
                print(test_case_object.name)

    return sorted(test_cases_per_file, key=lambda x: x.name, reverse=False)


# Generates the array of test cases from all the junit test reports in folder
def get_all_test_cases_from_xml_reports(junit_reports_folder, platform):
    if os.path.exists(junit_reports_folder):
        for filename in os.listdir(junit_reports_folder):
            if filename.lower().endswith(XML):
                print("File name: " + junit_reports_folder + '/' + filename)
                # Extend all_test_cases array with test cases from files in test results folder
                all_test_cases.extend(get_test_cases_per_file(junit_reports_folder + '/' + filename, platform))
        return all_test_cases
    else:
        return []


def get_test_run_details(junit_reports_folder, job_name, job_url, platform):
    tests = 0
    failures = 0
    skipped = 0
    time = 0
    if os.path.exists(junit_reports_folder):
        for filename in os.listdir(junit_reports_folder):
            if filename.lower().endswith(XML):
                print("File name - get_test_run_details: " + junit_reports_folder + '/' + filename)
                xml_doc = minidom.parse(junit_reports_folder + '/' + filename)

                if xml_doc.getElementsByTagName("testcase").__len__() > 0 and \
                        xml_doc.getElementsByTagName("testcase")[0].getAttribute("classname") == NO_TESTS_FOUND:
                    continue

                test_suites = xml_doc.getElementsByTagName(TEST_SUITE)
                for ts in test_suites:
                    # We don't care about milliseconds in time

                    try:
                        time_str = str(ts.attributes[TIME_ATTRIBUTE].value).split(".")
                    except KeyError:
                        time_str = "0.0"

                    tests += int(ts.attributes[TESTS].value)

                    try:
                        failures += int(ts.attributes[FAILURES].value)
                    except KeyError:
                        failures += 0

                    try:
                        skipped += int(ts.attributes[SKIPPED].value)
                    except KeyError:
                        skipped += 0

                    time += int(time_str[0])

    print(str(tests) + " " + str(skipped) + " " + str(failures) + " " + str(time))
    return TestRun(job_name, job_url, str(tests), str(failures), str(skipped), str(time), platform)


# parser jenkins job result xml
def get_duration_from_jenkins_job(result):
    xml = minidom.parseString(result)
    return int(xml.getElementsByTagName("timestamp")[0].firstChild.nodeValue)
