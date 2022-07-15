# Class that represents Jira issue


class TestRun:

    name = ''   # Test suite name
    url = ''   # Test job url
    failures = ''    # Failed test cases amount
    skipped = ''    # Skipped test cases amount
    time = ''   # Test suite run time
    platform = ''   # Test platform ios, android, web

    def __init__(self, name, url, tests, failures, skipped, time, platform):
        self.name = name
        self.url = url
        self.tests = tests
        self.failures = failures
        self.skipped = skipped
        self.time = time
        self.platform = platform
