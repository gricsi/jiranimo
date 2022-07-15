import json
from models.jira_issue import JiraIssue


# Jira API response parser for JiraIssue() object type. See issues JSON array response example below:
#
# {"issues": [
#         {
#             "expand": "operations,versionedRepresentations,editmeta,changelog,renderedFields",
#             "id": "208770",
#             "self": "https://jira.test.io/rest/api/2/issue/208770",
#             "key": "PM-57536",
#             "fields": {
#                 "status": {
#                     "self": "https://jira.test.io/rest/api/2/status/6",
#                     "description": "The issue is considered finished, the resolution is correct.
#                     Issues which are closed can be reopened.",
#                     "iconUrl": "https://jira.test.io/images/icons/statuses/closed.png",
#                     "name": "Closed",
#                     "id": "6"
#                 }
#             }
#         }
#     ]
# }
def parse_response(jira_issues_response):
    issues_list = []

    print (jira_issues_response)

    json_data = json.loads(jira_issues_response)
    issues = json_data["issues"]

    for issue in issues:
        key = issue["key"]
        status_id = issue["fields"]["status"]["id"]
        labels = issue["fields"]["labels"]
        if any("test_issue" in s for s in labels):
            issues_list.append(JiraIssue(key, status_id, True))
        elif any("flaky_test" in s for s in labels):
            issues_list.append(JiraIssue(key, status_id, False, True))
        else:
            issues_list.append(JiraIssue(key, status_id, False, False))

    return issues_list
