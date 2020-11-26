# JSM "large" dataset
Use following command to upload enterprise-scale "large" dataset to the Jira Service Management Data Center. 
This dataset is suitable for DC apps approval process performance test results generation.

#### JSM populate DB "large"
Populate DB from a postgres db dump:

`./app/util/jira/populate_db.sh --jsm`

#### JSM upload attachments "large"
Copy attachments:

`./app/util/jira/upload_attahcments.sh --jsm`

#### JSM index sync
To check if index successfully replicated to a new node after scaling event execute command on a new node:

`./app/util/jira/index-sync.sh`

# JSM "small dataset
There is also a `small` dataset available for JSM. This dataset is suitable for local 
Data Center Apps Performance Toolkit setup, testing and app-specific actions development.

#### JSM populate DB "small"
Populate DB from a postgres db dump:

`./app/util/jira/populate_db.sh --jsm --small`

#### JSM upload attachments "small"
Copy attachments:

`./app/util/jira/upload_attahcments.sh --jsm --small`