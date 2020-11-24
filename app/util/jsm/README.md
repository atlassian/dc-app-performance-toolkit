# JSD "large" dataset
Use following command to upload enterprise-scale "large" dataset to the Jira Service Desk Data Center. 
This dataset is suitable for DC apps approval process performance test results generation.

#### JSD populate DB "large"
Populate DB from a postgres db dump:

`./app/util/jira/populate_db.sh --jsd`

#### JSD upload attachments "large"
Copy attachments:

`./app/util/jira/upload_attahcments.sh --jsd`

#### JSD index sync
To check if index successfully replicated to a new node after scaling event execute command on a new node:

`./app/util/jira/index-sync.sh`

# JSD "small dataset
There is also a `small` dataset available for JSD. This dataset is suitable for local 
Data Center Apps Performance Toolkit setup, testing and app-specific actions development.

#### JSD populate DB "small"
Populate DB from a postgres db dump:

`./app/util/jira/populate_db.sh --jsd --small`

#### JSD upload attachments "small"
Copy attachments:

`./app/util/jira/upload_attahcments.sh --jsd --small`