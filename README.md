***jiranimo.py*** contains main script that is responsible for the whole parsing mechanism.

## Install Dependencies
- open command line and run `sudo pip install -r requirements.txt` 

It accepts four parameters:
1. Path to folder with test report(s)
2. Platform, i.e ***android, ios, web***
3. Job name - available in Jenkins job in ***JOB_NAME*** variable
4. Job url - available in Jenkins job in ***JOB_URL*** variable

## ENVIRONMENT Parameters 

- SLACK_CHANNEL 
- SLACK_HOOK
- JIRA_API_URL
- JIRA_USERNAME
- JIRA_PASSWORD
- JIRA_LINK - eg "https://jira.test.io/browse/"


***Example***:
`python jiranimo.py ./testcases/ android AndroidSmokeDE https://qaci.test.io/view/job/AndroidSmokeDE/5886/`
  
Jiranimo queries based on values in ***TestName*** field that was added to Jira ***Bug***, ***Customer Issue*** and ***Improvement*** issue types (https://jira.test.io/browse/CLOUD-10090).

