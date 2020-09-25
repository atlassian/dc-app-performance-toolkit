---
title: "Data Center App Performance Toolkit User Guide For Bitbucket"
platform: platform
product: marketplace
category: devguide
subcategory: build
date: "2020-02-13"
---
# Data Center App Performance Toolkit User Guide For Bitbucket

This document walks you through the process of testing your app on Bitbucket using the Data Center App Performance Toolkit. These instructions focus on producing the required [performance and scale benchmarks for your Data Center app](https://developer.atlassian.com/platform/marketplace/dc-apps-performance-and-scale-testing/).

To use the Data Center App Performance Toolkit, you'll need to:

1. [Set up Bitbucket Data Center on AWS](#instancesetup).
1. [Load an enterprise-scale dataset on your Bitbucket Data Center deployment](#preloading).
1. [Set up an execution environment for the toolkit](#executionhost).
1. [Run all the testing scenarios in the toolkit](#testscenario).

{{% note %}}
For simple spikes or tests, you can skip steps 1-2 and target any Bitbucket test instance. When you [set up your execution environment](#executionhost), you may need to edit the scripts according to your test instance's data set.
{{% /note %}}

## <a id="instancesetup"></a> Setting up Bitbucket Data Center

We recommend that you use the [AWS Quick Start for Bitbucket Data Center](https://aws.amazon.com/quickstart/architecture/bitbucket/) to deploy a Bitbucket Data Center testing environment. This Quick Start will allow you to deploy Bitbucket Data Center with a new [Atlassian Standard Infrastructure](https://aws.amazon.com/quickstart/architecture/atlassian-standard-infrastructure/) (ASI) or into an existing one.

The ASI is a Virtual Private Cloud (VPC) consisting of subnets, NAT gateways, security groups, bastion hosts, and other infrastructure components required by all Atlassian applications, and then deploys Bitbucket into this new VPC. Deploying Bitbucket with a new ASI takes around 50 minutes. With an existing one, it'll take around 30 minutes.

### Using the AWS Quick Start for Bitbucket

If you are a new user, perform an end-to-end deployment. This involves deploying Bitbucket into a _new_ ASI.

If you have already deployed the ASI separately by using the [ASI Quick Start](https://aws.amazon.com/quickstart/architecture/atlassian-standard-infrastructure/) or by deploying another Atlassian product (Jira, Bitbucket, or Confluence Data Center), deploy Bitbucket into your existing ASI.

{{% note %}}
You are responsible for the cost of the AWS services used while running this Quick Start reference deployment. There is no additional price for using this Quick Start. For more information, go to [aws.amazon.com/pricing](https://aws.amazon.com/ec2/pricing/).
{{% /note %}}

To reduce costs, we recommend you to keep your deployment up and running only during the performance runs.

### AWS cost estimation ###
[AWS Pricing Calculator](https://calculator.aws/) provides an estimate of usage charges for AWS services based on certain information you provide.
Monthly charges will be based on your actual usage of AWS services, and may vary from the estimates the Calculator has provided.

*The prices below are approximate and may vary depending on factors such as (region, instance type, deployment type of DB, etc.)

| Stack | Estimated hourly cost ($) |
| ----- | ------------------------- |
| One Node Bitbucket DC | 1.4 - 2.0 |
| Two Nodes Bitbucket DC | 1.7 - 2.5 |
| Four Nodes Bitbucket DC | 2.4 - 3.6 |

#### Stop Bitbucket cluster nodes
To reduce AWS infrastructure costs you could stop Bitbucket nodes when the cluster is standing idle.  
Bitbucket node might be stopped by using [Suspending and Resuming Scaling Processes](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-suspend-resume-processes.html).

To stop one node within the Bitbucket cluster follow the instructions:
1. Go to EC2 `Auto Scaling Groups` and open the necessary group to which belongs the node you want to stop.
1. Press `Edit` (in case you have New EC2 experience UI mode enabled, press `Edit` on `Advanced configuration`) and add `HealthCheck` to the `Suspended Processes`. Amazon EC2 Auto Scaling stops marking instances unhealthy as a result of EC2 and Elastic Load Balancing health checks.
1. Go to `Instances` and stop Bitbucket node.

To return Bitbucket node into a working state follow the instructions:  
1. Go to `Instances` and start Bitbucket node, wait a few minutes for Bitbucket node to become responsible.
1. Go to EC2 `Auto Scaling Groups` and open the necessary group to which belongs the node you want to start.
1. Press `Edit` (in case you have New EC2 experience UI mode enabled, press `Edit` on `Advanced configuration`) and remove `HealthCheck` from `Suspended Processes` of Auto Scaling Group.

#### <a id="quick-start-parameters"></a>  Quick Start parameters

All important parameters are listed and described in this section. For all other remaining parameters, we recommend using the Quick Start defaults.

**Bitbucket setup**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Version | 6.10.5 or 7.0.5 |

The Data Center App Performance Toolkit officially supports:

- Bitbucket Platform release version: 7.0.5
- Bitbucket [Long Term Support releases](https://confluence.atlassian.com/enterprise/atlassian-enterprise-releases-948227420.html): 6.10.5

**Cluster nodes**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Bitbucket cluster node instance type | [c5.2xlarge](https://aws.amazon.com/ec2/instance-types/c5/) |
| Maximum number of cluster nodes | 1 |
| Minimum number of cluster nodes | 1 |
| Cluster node instance volume size | 50 |

We recommend [c5.2xlarge](https://aws.amazon.com/ec2/instance-types/c5/) to strike the balance between cost and hardware we see in the field for our enterprise customers. More info could be found in public [recommendations](https://confluence.atlassian.com/enterprise/infrastructure-recommendations-for-enterprise-bitbucket-instances-on-aws-970602035.html).

The Data Center App Performance Toolkit framework is also set up for concurrency we expect on this instance size. As such, underprovisioning will likely show a larger performance impact than expected.

**File server**

| Parameter | Recommended Value |
| --------- | ----------------- |
| File server instance type | m4.xlarge |
| Home directory size | 1000 |


**Database**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Database instance class | [db.m4.large](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html#Concepts.DBInstanceClass.Summary) |
| RDS Provisioned IOPS | 1000 |
| Master password | Password1! |
| Enable RDS Multi-AZ deployment | false |
| Bitbucket database password | Password1! |
| Database storage | 100 |


{{% note %}}
The **Master (admin) password** will be used later when restoring the SQL database dataset. If password value is not set to default, you'll need to change `DB_PASS` value manually in the restore database dump script (later in [Preloading your Bitbucket deployment with an enterprise-scale dataset](#preloading)).
{{% /note %}}

**Elasticsearch**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Elasticsearch instance type | m4.xlarge.elasticsearch |
| Elasticsearch disk-space per node (GB) | 1000 |

**Networking (for new ASI)**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Trusted IP range | 0.0.0.0/0 _(for public access) or your own trusted IP range_ |
| Availability Zones | _Select two availability zones in your region_ |
| Permitted IP range | 0.0.0.0/0 _(for public access) or your own trusted IP range_ |
| Make instance internet facing | true |
| Key Name | _The EC2 Key Pair to allow SSH access. See [Amazon EC2 Key Pairs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html) for more info._ |

**Networking (for existing ASI)**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Make instance internet facing | true |
| Permitted IP range | 0.0.0.0/0 _(for public access) or your own trusted IP range_ |
| Key Name | _The EC2 Key Pair to allow SSH access. See [Amazon EC2 Key Pairs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html) for more info._ |

### Running the setup wizard

After successfully deploying Bitbucket Data Center in AWS, you'll need to configure it:

1. In the AWS console, go to **Services > CloudFormation > Stack > Stack details > Select your stack**.
1. On the **Outputs** tab, copy the value of the **LoadBalancerURL** key.
1. Open **LoadBalancerURL** in your browser. This will take you to the Bitbucket setup wizard.
1. On the **Bitbucket setup** page, populate the following fields:
    - **Application title**: any name for your Bitbucket Data Center deployment
    - **Base URL**: your stack's Elastic LoadBalancer URL
    - **License key**: select new evaluation license or existing license checkbox
    Click **Next**.
1. On the **Administrator account setup** page, populate the following fields:
    - **Username**: admin _(recommended)_
    - **Full name**: any full name of the admin user
    - **Email address**: email address of the admin user
    - **Password**: admin _(recommended)_
    - **Confirm Password**: admin _(recommended)_
    Click **Go to Bitbucket**.

{{% note %}}
After [Preloading your Bitbucket deployment with an enterprise-scale dataset](#preloading), the admin user will have `admin`/`admin` credentials.
{{% /note %}}

## <a id="preloading"></a> Preloading your Bitbucket deployment with an enterprise-scale dataset

Data dimensions and values for an enterprise-scale dataset are listed and described in the following table.

| Data dimensions | Value for an enterprise-scale dataset |
| --------------- | ------------------------------------- |
| Projects | ~25 000 |
| Repositories | ~52 000 |
| Users | ~25 000 |
| Pull Requests | ~ 1 000 000 |
| Total files number | ~750 000 |


{{% note %}}
All the datasets use the standard `admin`/`admin` credentials.
{{% /note %}}

Pre-loading the dataset is a three-step process:

1. [Importing the main dataset](#importingdataset). To help you out, we provide an enterprise-scale dataset you can import either via the [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/bitbucket/populate_db.sh) script or restore from xml backup file.
1. [Restoring attachments](#copyingattachments). We also provide attachments, which you can pre-load via an [upload_attachments.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/bitbucket/upload_attachments.sh) script.

The following subsections explain each step in greater detail.

### <a id="importingdataset"></a> Importing the main dataset

You can load this dataset directly into the database (via a [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/bitbucket/populate_db.sh) script).  

#### Loading the dataset via populate_db.sh script (~2 hours)

{{% note %}}
We recommend doing this via the CLI.
{{% /note %}}

To populate the database with SQL:

1. In the AWS console, go to **Services > EC2 > Instances**.
1. On the **Description** tab, do the following:
    - Copy the _Public IP_ of the Bastion instance.
    - Copy the _Private IP_ of the Bitbucket node instance.
    - Copy the _Private IP_ of the Bitbucket NFS Server instance.
1. Using SSH, connect to the Bitbucket node via the Bastion instance:

    For Windows, use Putty to connect to the Bitbucket node over SSH.
    For Linux or MacOS:
    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NODE_IP=node_private_ip
    export SSH_OPTS='-o ServerAliveInterval=60 -o ServerAliveCountMax=30'
    ssh ${SSH_OPTS} -o "proxycommand ssh -W %h:%p ${SSH_OPTS} ec2-user@${BASTION_IP}" ec2-user@${NODE_IP}
    ```
    For more information, go to [Connecting your nodes over SSH](https://confluence.atlassian.com/adminjiraserver/administering-jira-data-center-on-aws-938846969.html#AdministeringJiraDataCenteronAWS-ConnectingtoyournodesoverSSH).
1. Stop Bitbucket Server:

    ``` bash
    sudo systemctl stop bitbucket
    ```
1. In a new terminal session connect to the Bitbucket NFS Server over SSH:

    For Windows, use Putty to connect to the Bitbucket node over SSH.
    For Linux or MacOS:
    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NFS_SERVER_IP=nfs_server_private_ip
    export SSH_OPTS='-o ServerAliveInterval=60 -o ServerAliveCountMax=30'
    ssh ${SSH_OPTS} -o "proxycommand ssh -W %h:%p ${SSH_OPTS} ec2-user@${BASTION_IP}" ec2-user@${NFS_SERVER_IP}
    ```
    For more information, go to [Connecting your nodes over SSH](https://confluence.atlassian.com/adminjiraserver/administering-jira-data-center-on-aws-938846969.html#AdministeringJiraDataCenteronAWS-ConnectingtoyournodesoverSSH).

1. Download the [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/bitbucket/populate_db.sh) script and make it executable:

    ``` bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/bitbucket/populate_db.sh && chmod +x populate_db.sh
    ```
1. Review the following `Variables section` of the script:

    ``` bash
    INSTALL_PSQL_CMD="amazon-linux-extras install -y postgresql10"
    DB_CONFIG="/media/atl/bitbucket/shared/bitbucket.properties"

    # Depending on BITBUCKET installation directory
    BITBUCKET_CURRENT_DIR="/opt/atlassian/bitbucket/current/"
    BITBUCKET_VERSION_FILE="/media/atl/bitbucket/shared/bitbucket.version"

    # DB admin user name, password and DB name
    BITBUCKET_DB_NAME="bitbucket"
    BITBUCKET_DB_USER="postgres"
    BITBUCKET_DB_PASS="Password1!"

    # Datasets AWS bucket and db dump name
    DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/bitbucket"
    DATASETS_SIZE="large"
    ```
1. Run the script:

    ``` bash
    ./populate_db.sh | tee -a populate_db.log
    ```

{{% note %}}
Do not close or interrupt the session. It will take about an hour to restore SQL database. When SQL restoring is finished, an admin user will have `admin`/`admin` credentials.

In case of a failure, check the `Variables` section and run the script one more time.
{{% /note %}}

### <a id="copyingattachments"></a> Restoring attachments (~2 hours)

After [Importing the main dataset](#importingdataset), you'll now have to pre-load an enterprise-scale set of attachments.

1. Using SSH, connect to the Bitbucket NFS Server via the Bastion instance:

    For Windows, use Putty to connect to the Bitbucket node over SSH.
    For Linux or MacOS:
    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NFS_SERVER_IP=nfs_server_private_ip
    export SSH_OPTS='-o ServerAliveInterval=60 -o ServerAliveCountMax=30'
    ssh ${SSH_OPTS} -o "proxycommand ssh -W %h:%p ${SSH_OPTS} ec2-user@$BASTION_IP" ec2-user@${NFS_SERVER_IP}
    ```
    For more information, go to [Connecting your nodes over SSH](https://confluence.atlassian.com/adminjiraserver/administering-jira-data-center-on-aws-938846969.html#AdministeringJiraDataCenteronAWS-ConnectingtoyournodesoverSSH).
1. Download the [upload_attachments.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/bitbucket/upload_attachments.sh) script and make it executable:

    ``` bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/bitbucket/upload_attachments.sh && chmod +x upload_attachments.sh
    ```    
1. Review the following `Variables section` of the script:

    ``` bash
    DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/bitbucket"
    ATTACHMENTS_TAR="attachments.tar.gz"
    DATASETS_SIZE="large"
    ATTACHMENTS_TAR_URL="${DATASETS_AWS_BUCKET}/${BITBUCKET_VERSION}/${DATASETS_SIZE}/${ATTACHMENTS_TAR}"
    NFS_DIR="/media/atl/bitbucket/shared"
    ATTACHMENT_DIR_DATA="data"
    ```
1. Run the script:

    ``` bash
    ./upload_attachments.sh | tee -a upload_attachments.log
    ```

{{% note %}}
Do not close or interrupt the session. It will take about two hours to upload attachments.
{{% /note %}}


### Start Bitbucket Server
1. Using SSH, connect to the Bitbucket node via the Bastion instance:

    For Windows, use Putty to connect to the Bitbucket node over SSH.
    For Linux or MacOS:
    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NODE_IP=node_private_ip
    export SSH_OPTS='-o ServerAliveInterval=60 -o ServerAliveCountMax=30'
    ssh ${SSH_OPTS} -o "proxycommand ssh -W %h:%p ${SSH_OPTS} ec2-user@${BASTION_IP}" ec2-user@${NODE_IP}
    ```
    For more information, go to [Connecting your nodes over SSH](https://confluence.atlassian.com/adminjiraserver/administering-jira-data-center-on-aws-938846969.html#AdministeringJiraDataCenteronAWS-ConnectingtoyournodesoverSSH).
1. Start Bitbucket Server:

    ``` bash
    sudo systemctl start bitbucket
    ```
1. Wait 10-15 minutes until Bitbucket Server is started.

### Elasticsearch Index
If your app does not use Bitbucket search functionality just **skip** this section.

Otherwise, if your app is depending on Bitbucket search functionality you need to wait until Elasticsearch index is finished.
**Bitbucket-project** index and **bitbucket-repository** index usually take about 10 hours on a User Guide [recommended configuration](#quick-start-parameters), **bitbucket-search** index (search by repositories content) could take up to a couple of days.

To check status of indexing:

1. Open **LoadBalancerURL** in your browser.
1. Login with admin user.
1. Navigate to `LoadBalancerURL/rest/indexing/latest/status` page:

    `"status":"INDEXING"` - index is in progress

    `"status":"IDLE"` - index is finished

{{% note %}}
In case of any difficulties with Index generation, contact us for support in the [community Slack](http://bit.ly/dcapt_slack) **#data-center-app-performance-toolkit** channel.
{{% /note %}}

## <a id="executionhost"></a> Setting up an execution environment

{{% note %}}
For simple spikes or tests, you can set up an execution environment on your local machine. To do this, clone the [DC App Performance Toolkit repo](https://github.com/atlassian/dc-app-performance-toolkit) and follow the instructions on the `dc-app-performance-toolkit/README.md` file. Make sure your local machine has at least a 4-core CPU and 16GB of RAM.
{{% /note %}}  

If you're using the DC App Performance Toolkit to produce the required [performance and scale benchmarks for your Data Center app](https://developer.atlassian.com/platform/marketplace/dc-apps-performance-and-scale-testing/), we recommend that you set up your execution environment on AWS:

1. [Launch AWS EC2 instance](https://docs.aws.amazon.com/quickstarts/latest/vmlaunch/step-1-launch-instance.html). Instance type: [`c5.2xlarge`](https://aws.amazon.com/ec2/instance-types/c5/), OS: select from Quick Start `Ubuntu Server 18.04 LTS`.
1. Connect to the instance using [SSH](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html) or the [AWS Systems Manager Sessions Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html).

    ```bash
    ssh -i path_to_pem_file ubuntu@INSTANCE_PUBLIC_IP
    ```

1. Install [Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository). Setup manage Docker as a [non-root user](https://docs.docker.com/engine/install/linux-postinstall).
1. Go to GitHub and create a fork of [dc-app-performance-toolkit](https://github.com/atlassian/dc-app-performance-toolkit).
1. Clone the fork locally, then edit the `bitbucket.yml` configuration file and other files as needed.
1. Push your changes to the forked repository.
1. Connect to the AWS EC2 instance and clone forked repository.

Once your environment is set up, you can run the DC App Performance Toolkit:

``` bash
cd dc-app-performance-toolkit
docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt bitbucket.yml
```

You'll need to run the toolkit for each [test scenario](#testscenario) in the next section.

## <a id="testscenario"></a> Running the test scenarios on your execution environment

Using the Data Center App Performance Toolkit for [Performance and scale testing your Data Center app](/platform/marketplace/developing-apps-for-atlassian-data-center-products/) involves two test scenarios:

- [Performance regression](#testscenario1)
- [Scalability testing](#testscenario2)

Each scenario will involve multiple test runs. The following subsections explain both in greater detail.

### <a id="testscenario1"></a> Scenario 1: Performance regression

This scenario helps to identify basic performance issues without a need to spin up a multi-node Bitbucket DC. Make sure the app does not have any performance impact when it is not exercised.

#### <a id="regressionrun1"></a> Run 1 (~1 hour)

To receive performance baseline results without an app installed:

1. On the computer where you cloned the Data Center App Performance Toolkit, navigate to `dc-app-performance-toolkit/app folder`.
1. Open the `bitbucket.yml` file and fill in the following variables:
    - `application_hostname`: your_dc_bitbucket_instance_hostname without protocol
    - `application_protocol`: HTTP or HTTPS
    - `application_port`: for HTTP - 80, for HTTPS - 443, or your instance-specific port. The self-signed certificate is not supported.
    - `admin_login`: admin user username
    - `admin_password`: admin user password
    - `concurrency`: number of concurrent users for JMeter scenario - we recommend you use the defaults to generate full-scale results.
    - `test_duration`: duration of the performance run - we recommend you use the defaults to generate full-scale results.
    - `ramp-up`: amount of time it will take JMeter to add all test users to test execution - we recommend you use the defaults to generate full-scale results.
1. Run bzt.

    ``` bash
    bzt bitbucket.yml
    ```
1. View the following main results of the run in the `dc-app-performance-toolkit/app/results/bitbucket/YY-MM-DD-hh-mm-ss` folder:
    - `results_summary.log`: detailed run summary
    - `results.csv`: aggregated .csv file with all actions and timings
    - `bzt.log`: logs of the Taurus tool execution
    - `jmeter.*`: logs of the JMeter tool execution
    - `pytest.*`: logs of Pytest-Selenium execution

{{% note %}}
When the execution is successfully completed, the `INFO: Artifacts dir:` line with the full path to results directory will be displayed in console output. Save this full path to the run results folder. Later you will have to insert it under `runName: "without app"` for report generation.
{{% /note %}}

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps.
{{% /note %}}


#### <a id="regressionrun2"></a> Run 2 (~1 hour)

To receive performance results with an app installed:

1. Install the app you want to test.
1. Run bzt.

    ``` bash
    bzt bitbucket.yml
    ```

{{% note %}}
When the execution is successfully completed, the `INFO: Artifacts dir:` line with the full path to results directory will be displayed in console output. Save this full path to the run results folder. Later you will have to insert it under `runName: "with app"` for report generation.
{{% /note %}}

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps.
{{% /note %}}


#### Generating a performance regression report

To generate a performance regression report:  

1. Navigate to the `dc-app-performance-toolkit/app/reports_generation` folder.
1. Edit the `performance_profile.yml` file:
    - Under `runName: "without app"`, in the `fullPath` key, insert the full path to results directory of [Run 1](#regressionrun1).
    - Under `runName: "with app"`, in the `fullPath` key, insert the full path to results directory of [Run 2](#regressionrun2).
1. Run the following command:

    ``` bash
    python csv_chart_generator.py performance_profile.yml
    ```
1. In the `dc-app-performance-toolkit/app/results/reports/YY-MM-DD-hh-mm-ss` folder, view the `.csv` file (with consolidated scenario results), the `.png` chart file and summary report.

#### Analyzing report

Once completed, you will be able to review the action timings with and without your app to see its impact on the performance of the instance. If you see a significant impact (>10%) on any action timing, we recommend taking a look into the app implementation to understand the root cause of this delta.


### <a id="testscenario2"></a> Scenario 2: Scalability testing

The purpose of scalability testing is to reflect the impact on the customer experience when operating across multiple nodes. For this, you have to run scale testing on your app.

For many apps and extensions to Atlassian products, there should not be a significant performance difference between operating on a single node or across many nodes in Bitbucket DC deployment. To demonstrate performance impacts of operating your app at scale, we recommend testing your Bitbucket DC app in a cluster.

#### Extending the base action

Extension scripts, which extend the base Selenium (`bitbucket-ui.py`) scripts, are located in a separate folder (`dc-app-performance-toolkit/extension/bitbucket`). You can modify these scripts to include their app-specific actions.

##### Modifying Selenium

You can extend Selenium scripts to measure the end-to-end browser timings.

We use **Pytest** to drive Selenium tests. The `bitbucket-ui.py` executor script is located in the `app/selenium_ui/` folder. This file contains all browser actions, defined by the `test_ functions`. These actions are executed one by one during the testing.

In the `bitbucket-ui.py` script, view the following block of code:

``` python
# def test_1_selenium_custom_action(webdriver, datasets, screen_shots):
#     app_specific_action(webdriver, datasets)
```

This is a placeholder to add an extension action. The custom action can be moved to a different line, depending on the required workflow, as long as it is between the login (`test_0_selenium_a_login`) and logout (`test_2_selenium_z_log_out`) actions.

To implement the app_specific_action function, modify the `extension_ui.py` file in the `extension/bitbucket/` directory. The following is an example of the `app_specific_action` function, where Selenium navigates to a URL, clicks on an element, and waits until an element is visible.

To view more examples, see the `modules.py` file in the `selenium_ui/bitbucket` directory.

#### Running tests with your modification

To ensure that the test runs without errors in parallel, run your extension scripts with the base scripts as a sanity check.

##### <a id="run3"></a> Run 3 (~1 hour)
To receive scalability benchmark results for one-node Bitbucket DC with app-specific actions, run `bzt`:

``` bash
bzt bitbucket.yml
```

{{% note %}}
When the execution is successfully completed, the `INFO: Artifacts dir:` line with the full path to results directory will be displayed.
Save this full path to the run results folder. Later you will have to insert it under `runName: "Node 1"` for report generation.
{{% /note %}}

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps.
{{% /note %}}


##### <a id="run4"></a> Run 4 (~1 hour)

To receive scalability benchmark results for two-node Bitbucket DC with app-specific actions:

1. In the AWS console, go to **CloudFormation > Stack details > Select your stack**.
1. On the **Update** tab, select **Use current template**, and then click **Next**.
1. Enter `2` in the **Maximum number of cluster nodes** and the **Minimum number of cluster nodes** fields.
1. Click **Next > Next > Update stack** and wait until stack is updated.
1. Run bzt.

    ``` bash
    bzt bitbucket.yml
    ```    

{{% note %}}
When the execution is successfully completed, the `INFO: Artifacts dir:` line with the full path to results directory will be displayed in console output. Save this full path to the run results folder. Later you will have to insert it under `runName: "Node 2"` for report generation.
{{% /note %}}

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps.
{{% /note %}}


##### <a id="run5"></a> Run 5 (~1 hour)

To receive scalability benchmark results for four-node Bitbucket DC with app-specific actions:

1. Scale your Bitbucket Data Center deployment to 4 nodes the same way as in [Run 4](#run4).
1. Run bzt.

    ``` bash
    bzt bitbucket.yml
    ```    

{{% note %}}
When the execution is successfully completed, the `INFO: Artifacts dir:` line with the full path to results directory will be displayed in console output.
Save this full path to the run results folder. Later you will have to insert it under `runName: "Node 4"` for report generation.
{{% /note %}}

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps.
{{% /note %}}


#### Generating a report for scalability scenario

To generate a scalability report:

1. Navigate to the `dc-app-performance-toolkit/app/reports_generation` folder.
1. Edit the `scale_profile.yml` file:
    - For `runName: "Node 1"`, in the `fullPath` key, insert the full path to results directory of [Run 3](#run3).
    - For `runName: "Node 2"`, in the `fullPath` key, insert the full path to results directory of [Run 4](#run4).
    - For `runName: "Node 4"`, in the `fullPath` key, insert the full path to results directory of [Run 5](#run5).
1. Run the following command:

    ``` bash
    python csv_chart_generator.py scale_profile.yml
    ```
1. In the `dc-app-performance-toolkit/app/results/reports/YY-MM-DD-hh-mm-ss` folder, view the `.csv` file (with consolidated scenario results), the `.png` chart file and summary report.

#### Analyzing report

Once completed, you will be able to review action timings on Bitbucket Data Center with different numbers of nodes. If you see a significant variation in any action timings between configurations, we recommend taking a look into the app implementation to understand the root cause of this delta.

After completing all your tests, delete your Bitbucket Data Center stacks.


## Support
In case of technical questions, issues or problems with DC Apps Performance Toolkit, contact us for support in the [community Slack](http://bit.ly/dcapt_slack) **#data-center-app-performance-toolkit** channel.
