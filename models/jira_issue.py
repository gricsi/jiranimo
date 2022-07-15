# Class that represents Jira issue
class JiraIssue:
    key = ''
    state = ''
    is_test_issue = False
    is_flaky_test_issue = False

    def __init__(self, key, state, is_test_issue, is_flaky_test_issue=False):
        self.key = key
        self.state = state
        self.is_test_issue = is_test_issue
        self.is_flaky_test_issue = is_flaky_test_issue
