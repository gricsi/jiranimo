# Class that represents TestCase object
class TestCase:
    name = ''  # Test case name
    class_name = ''  # Test case name
    is_successful = None  # Pass/Fail boolean value
    time = ''  # Test case run time
    age = ''  # Test case age - Jenkins keeps track of the age of test failures
    jira_issues = []  # An array of JiraIssue() objects per test case
    link = ''  # Test result link for the slack report
    slack_report_name = ''  # ClassName.TestName used in slack reporting
    stack_trace = ""

    def __init__(self, name, class_name, time, age, is_successful, stacktrace, jira_issues=None):
        if jira_issues is None:
            jira_issues = []
        self.name = name
        self.class_name = class_name
        self.is_successful = is_successful
        self.time = time
        self.age = age
        self.jira_issues = jira_issues
        class_name_without_package = ''.join(reversed(class_name)).split('.')[0]
        self.slack_report_name = "*{0}* {1}".format(''.join(reversed(class_name_without_package)), name)
        self.stacktrace = stacktrace

        if class_name.find('.') != -1:
            k = class_name.rfind(".")
            name = name.replace("[", "_") \
                .replace("]", "_") \
                .replace(":", "_") \
                .replace("()", "__") \
                .replace("{", "_") \
                .replace("}", "_")

            self.link = "{0}/{1}/{2}".format(class_name[:k], class_name[k + 1:], name)
        else:
            self.link = "{0}/{1}".format(class_name, name.replace("()", "__"))

    def add_jira_issues(self, issues):
        self.jira_issues.append(issues)

    def get_jira_issues(self):
        return self.jira_issues

    def update_age(self, age):
        self.age = age
