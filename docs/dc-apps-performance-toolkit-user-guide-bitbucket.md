---
title: "Data Center App Performance Toolkit User Guide For Bitbucket"
platform: platform
product: marketplace
category: devguide
subcategory: build
date: "2021-11-17"
---
# Data Center App Performance Toolkit User Guide For Bitbucket

This document walks you through the process of testing your app on Bitbucket using the Data Center App Performance Toolkit. These instructions focus on producing the required [performance and scale benchmarks for your Data Center app](https://developer.atlassian.com/platform/marketplace/dc-apps-performance-and-scale-testing/).

In this document, we cover the use of the Data Center App Performance Toolkit on two types of environments:

**[Development environment](#mainenvironmentdev)**: Bitbucket Data Center environment for a test run of Data Center App Performance Toolkit and development of [app-specific actions](#appspecificactions). We recommend you use the [AWS Quick Start for Bitbucket Data Center](https://aws.amazon.com/quickstart/architecture/bitbucket/) with the parameters prescribed here.

1. [Set up a development environment Bitbucket Data Center on AWS](#devinstancesetup).
2. [Create a dataset for the development environment](#devdataset).
3. [Run toolkit on the development environment locally](#devtestscenario).
4. [Develop and test app-specific actions locally](#devappaction).

**[Enterprise-scale environment](#mainenvironmententerprise)**: Bitbucket Data Center environment used to generate Data Center App Performance Toolkit test results for the Marketplace approval process. Preferably, use the [AWS Quick Start for Bitbucket Data Center](https://aws.amazon.com/quickstart/architecture/bitbucket/) with the parameters prescribed below. These parameters provision larger, more powerful infrastructure for your Bitbucket Data Center.

5. [Set up an enterprise-scale environment Bitbucket Data Center on AWS](#instancesetup).
6. [Load an enterprise-scale dataset on your Bitbucket Data Center deployment](#preloading).
7. [Set up an execution environment for the toolkit](#executionhost).
8. [Run all the testing scenarios in the toolkit](#testscenario).

{{% note %}}
For simple spikes or tests, you can skip steps 1-2 and target any Bitbucket test instance. When you [set up your execution environment](#executionhost), you may need to edit the scripts according to your test instance's data set.
{{% /note %}}

---

## <a id="mainenvironmentdev"></a>Development environment

Running the tests in a development environment helps familiarize you with the toolkit. It'll also provide you with a lightweight and less expensive environment for developing. Once you're ready to generate test results for the Marketplace Data Center Apps Approval process, run the toolkit in an **enterprise-scale environment**.

### <a id="devinstancesetup"></a>1. Setting up Bitbucket Data Center development environment

We recommend that you set up development environment using the [AWS Quick Start for Bitbucket Data Center](https://aws.amazon.com/quickstart/architecture/bitbucket/) (**How to deploy** tab). All the instructions on this page are optimized for AWS. If you already have an existing Bitbucket Data Center environment, you can also use that too (if so, skip to [Create a dataset for the development environment](#devdataset)).

#### Using the AWS Quick Start for Bitbucket

If you are a new user, perform an end-to-end deployment. This involves deploying Bitbucket into a _new_ ASI:

Navigate to **[AWS Quick Start for Bitbucket Data Center](https://aws.amazon.com/quickstart/architecture/bitbucket/) &gt; How to deploy** tab **&gt; Deploy into a new ASI** link.

If you have already deployed the ASI separately by using the [ASI Quick Start](https://aws.amazon.com/quickstart/architecture/atlassian-standard-infrastructure/)ASI Quick Start or by deploying another Atlassian product (Jira, Bitbucket, or Confluence Data Center development environment) with ASI, deploy Bitbucket into your existing ASI:

Navigate to **[AWS Quick Start for Bitbucket Data Center](https://aws.amazon.com/quickstart/architecture/bitbucket/) &gt; How to deploy** tab **&gt; Deploy into your existing ASI** link.

{{% note %}}
You are responsible for the cost of AWS services used while running this Quick Start reference deployment. This Quick Start doesn't have any additional prices. See [Amazon EC2 pricing](https://aws.amazon.com/ec2/pricing/) for more detail.
{{% /note %}}

To reduce costs, we recommend you to keep your deployment up and running only during the performance runs.

#### AWS cost estimation for the development environment

AWS Bitbucket Data Center development environment infrastructure costs about 25 - 40$ per working week depending on such factors like region, instance type, deployment type of DB, and other.  

#### <a id="quick-start-parameters"></a> Quick Start parameters for development environment

All important parameters are listed and described in this section. For all other remaining parameters, we recommend using the Quick Start defaults.

**Bitbucket setup**

| Parameter | Recommended value |
| --------- | ----------------- |
| Bitbucket Product | Software |
| Version | The Data Center App Performance Toolkit officially supports `7.6.10`, `7.17.1` ([Long Term Support releases](https://confluence.atlassian.com/enterprise/atlassian-enterprise-releases-948227420.html)) |

**Cluster nodes**

| Parameter | Recommended value |
| --------- | ----------------- |
| Cluster node instance type | [t3.medium](https://aws.amazon.com/ec2/instance-types/t3/) (we recommend this instance type for its good balance between price and performance in testing environments) |
| Maximum number of cluster nodes | 1 |
| Minimum number of cluster nodes | 1 |
| Cluster node instance volume size | 50 |

**File server**

| Parameter | Recommended Value |
| --------- | ----------------- |
| File server instance type | m4.xlarge |
| Home directory size | 100 |


**Database**

| Parameter | Recommended Value |
| --------- | ----------------- |
| The database engine to deploy with | PostgresSQL |
| The database engine version to use | 11 |
| Database instance class | [db.t3.medium](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html#Concepts.DBInstanceClass.Summary) |
| RDS Provisioned IOPS | 1000 |
| Master password | Password1! |
| Enable RDS Multi-AZ deployment | false |
| Bitbucket database password | Password1! |
| Database storage | 100 |

**Elasticsearch**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Elasticsearch master user password | (leave blank) |
| Elasticsearch instance type | m4.large.elasticsearch |
| Elasticsearch disk-space per node (GB) | 100 |

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

1. In the AWS console, go to **Services** > **CloudFormation** > **Stack** > **Stack details** > **Select your stack**.
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

---

### <a id="devdataset"></a>2. Generate dataset for development environment  

After creating the development environment Bitbucket Data Center, generate test dataset to run Data Center App Performance Toolkit:
- Create at least one project
- Create repository with some files in a project
- Create a new branch from the repo, make and push changes to the branch and create a pull request

---

### <a id="devtestscenario"></a>3. Run toolkit on the development environment locally

{{% warning %}}
Make sure **English (United States)** language is selected as a default language on the **![cog icon](/platform/marketplace/images/cog.png) &gt; Server settings &gt; Language** page. Other languages are **not supported** by the toolkit.
{{% /warning %}}

1. Clone [Data Center App Performance Toolkit](https://github.com/atlassian/dc-app-performance-toolkit) locally.
1. Follow the [README.md](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/README.md) instructions to set up toolkit locally.
1. Navigate to `dc-app-performance-toolkit/app` folder.
1. Open the `bitbucket.yml` file and fill in the following variables:
    - `application_hostname`: your_dc_bitbucket_instance_hostname without protocol.
    - `application_protocol`: http or https.
    - `application_port`: for HTTP - 80, for HTTPS - 443, 8080, 7990 or your instance-specific port.
    - `secure`: True or False. Default value is True. Set False to allow insecure connections, e.g. when using self-signed SSL certificate.
    - `application_postfix`: it is empty by default; e.g., /bitbucket for url like this http://localhost:7990/bitbucket.
    - `admin_login`: admin user username.
    - `admin_password`: admin user password.
    - `load_executor`: executor for load tests - [jmeter](https://jmeter.apache.org/)
    - `concurrency`: `1` - number of concurrent JMeter users.
    - `test_duration`: `5m` - duration of the performance run.
    - `ramp-up`: `1s` - amount of time it will take JMeter to add all test users to test execution.
    - `total_actions_per_hour`: `3270` - number of total JMeter actions per hour.
    - `WEBDRIVER_VISIBLE`: visibility of Chrome browser during selenium execution (False is by default).
    
1. Run bzt.

    ``` bash
    bzt bitbucket.yml
    ```

1. Review the resulting table in the console log. All JMeter and Selenium actions should have 95+% success rate.  
In case some actions does not have 95+% success rate refer to the following logs in `dc-app-performance-toolkit/app/results/bitbucket/YY-MM-DD-hh-mm-ss` folder:

    - `results_summary.log`: detailed run summary
    - `results.csv`: aggregated .csv file with all actions and timings
    - `bzt.log`: logs of the Taurus tool execution
    - `jmeter.*`: logs of the JMeter tool execution
    - `pytest.*`: logs of Pytest-Selenium execution

{{% warning %}}
Do not proceed with the next step until you have all actions 95+% success rate. Ask [support](#support) if above logs analysis did not help.
{{% /warning %}}

---

### <a id="devappaction"></a>4. Develop and test app-specific action locally
Data Center App Performance Toolkit has its own set of default test actions for Bitbucket Data Center: JMeter and Selenium for load and UI tests respectively.     

**App-specific action** - action (performance test) you have to develop to cover main use cases of your application. Performance test should focus on the common usage of your application and not to cover all possible functionality of your app. For example, application setup screen or other one-time use cases are out of scope of performance testing.

1. Define main use case of your app. Usually it is one or two main app use cases.
1. Your app adds new UI elements in Bitbucket Data Center - Selenium app-specific action has to be developed.
1. Your app introduces new endpoint or extensively calls existing Bitbucket Data Center API - JMeter app-specific actions has to be developed.  


{{% note %}}
We strongly recommend developing your app-specific actions on the development environment to reduce AWS infrastructure costs.
{{% /note %}}

#### Example of app-specific Selenium action development
You develop an app that adds some additional fields to specific types of Bitbucket issues. In this case, you should develop Selenium app-specific action:

1. Extend example of app-specific action in `dc-app-performance-toolkit/app/extension/bitbucket/extension_ui.py`.  
[Code example.](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/extension/bitbucket/extension_ui.py)
So, our test has to open app-specific issues and measure time to load of this app-specific issues.
1. If you need to run `app_speicifc_action` as specific user uncomment `app_specific_user_login` function in [code example](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/extension/bitbucket/extension_ui.py). Note, that in this case `test_1_selenium_custom_action` should follow just before `test_2_selenium_z_log_out` action.
1. In `dc-app-performance-toolkit/app/selenium_ui/bitbucket-ui.py`, review and uncomment the following block of code to make newly created app-specific actions executed:
``` python
# def test_1_selenium_custom_action(webdriver, datasets, screen_shots):
#     app_specific_action(webdriver, datasets)
```

4. Run toolkit with `bzt bitbucket.yml` command to ensure that all Selenium actions including `app_specific_action` are successful.

## <a id="mainenvironmententerprise"></a> Enterprise-scale environment

After adding your custom app-specific actions, you should now be ready to run the required tests for the Marketplace Data Center Apps Approval process. To do this, you'll need an **enterprise-scale environment**.

### <a id="instancesetup"></a>5. Set up an enterprise-scale environment Bitbucket Data Center on AWS

We recommend that you use the [AWS Quick Start for Bitbucket Data Center](https://aws.amazon.com/quickstart/architecture/bitbucket/) (**How to deploy** tab) to deploy a Bitbucket Data Center testing environment. This Quick Start will allow you to deploy Bitbucket Data Center with a new [Atlassian Standard Infrastructure](https://aws.amazon.com/quickstart/architecture/atlassian-standard-infrastructure/) (ASI) or into an existing one.

The ASI is a Virtual Private Cloud (VPC) consisting of subnets, NAT gateways, security groups, bastion hosts, and other infrastructure components required by all Atlassian applications, and then deploys Bitbucket into this new VPC. Deploying Bitbucket with a new ASI takes around 50 minutes. With an existing one, it'll take around 30 minutes.

### Using the AWS Quick Start for Bitbucket

If you are a new user, perform an end-to-end deployment. This involves deploying Bitbucket into a _new_ ASI:

Navigate to **[AWS Quick Start for Bitbucket Data Center](https://aws.amazon.com/quickstart/architecture/bitbucket/) &gt; How to deploy** tab **&gt; Deploy into a new ASI** link.

If you have already deployed the ASI separately by using the [ASI Quick Start](https://aws.amazon.com/quickstart/architecture/atlassian-standard-infrastructure/)ASI Quick Start or by deploying another Atlassian product (Jira, Bitbucket, or Confluence Data Center development environment) with ASI, deploy Bitbucket into your existing ASI:

Navigate to **[AWS Quick Start for Bitbucket Data Center](https://aws.amazon.com/quickstart/architecture/bitbucket/) &gt; How to deploy** tab **&gt; Deploy into your existing ASI** link.

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

#### Stop cluster nodes

To reduce AWS infrastructure costs you could stop cluster nodes when the cluster is standing idle.  
Cluster node might be stopped by using [Suspending and Resuming Scaling Processes](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-suspend-resume-processes.html).

To stop one node within the cluster, follow the instructions below:

1. In the AWS console, go to **Services** > **EC2** > **Auto Scaling Groups** and open the necessary group to which belongs the node you want to stop.
1. Click **Edit** (in case you have New EC2 experience UI mode enabled, press `Edit` on `Advanced configuration`) and add `HealthCheck` to the `Suspended Processes`. Amazon EC2 Auto Scaling stops marking instances unhealthy as a result of EC2 and Elastic Load Balancing health checks.
1. Go to EC2 **Instances**, select instance, click **Instance state** > **Stop instance**.

To return node into a working state follow the instructions:  

1. Go to EC2 **Instances**, select instance, click **Instance state** > **Start instance**, wait a few minutes for node to become available.
1. Go to EC2 **Auto Scaling Groups** and open the necessary group to which belongs the node you want to start.
1. Press **Edit** (in case you have New EC2 experience UI mode enabled, press `Edit` on `Advanced configuration`) and remove `HealthCheck` from `Suspended Processes` of Auto Scaling Group.

#### Stop database

To reduce AWS infrastructure costs database could be stopped when the cluster is standing idle.
Keep in mind that database would be **automatically started** in **7** days.

To stop database:

1. In the AWS console, go to **Services** > **RDS** > **Databases**.
1. Select cluster database.
1. Click on **Actions** > **Stop**.

To start database:

1. In the AWS console, go to **Services** > **RDS** > **Databases**.
1. Select cluster database.
1. Click on **Actions** > **Start**.

#### <a id="quick-start-parameters"></a>  Quick Start parameters

All important parameters are listed and described in this section. For all other remaining parameters, we recommend using the Quick Start defaults.

**Bitbucket setup**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Version | The Data Center App Performance Toolkit officially supports `7.6.10`, `7.17.1` ([Long Term Support releases](https://confluence.atlassian.com/enterprise/atlassian-enterprise-releases-948227420.html)) |


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
| The database engine to deploy with | PostgresSQL |
| The database engine version to use | 11 |
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
| Elasticsearch master user password | (leave blank) |
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

1. In the AWS console, go to **Services** > **CloudFormation** > **Stack** > **Stack details** > **Select your stack**.
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

---

### <a id="preloading"></a>6. Preloading your Bitbucket deployment with an enterprise-scale dataset

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

Pre-loading the dataset is a two-step process:

1. [Importing the main dataset](#importingdataset). To help you out, we provide an enterprise-scale dataset you can import either via the [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/bitbucket/populate_db.sh).
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

    For Linux or MacOS run following commands in terminal (for Windows use [Git Bash](https://git-scm.com/downloads) terminal):
    
    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NODE_IP=node_private_ip
    export SSH_OPTS1='-o ServerAliveInterval=60'
    export SSH_OPTS2='-o ServerAliveCountMax=30'
    ssh ${SSH_OPTS1} ${SSH_OPTS2} -o "proxycommand ssh -W %h:%p ${SSH_OPTS1} ${SSH_OPTS2} ec2-user@${BASTION_IP}" ec2-user@${NODE_IP}
    ```
    For more information, go to [Connecting your nodes over SSH](https://confluence.atlassian.com/adminjiraserver/administering-jira-data-center-on-aws-938846969.html#AdministeringJiraDataCenteronAWS-ConnectingtoyournodesoverSSH).
1. Stop Bitbucket Server:

    ``` bash
    sudo systemctl stop bitbucket
    ```
1. In a new terminal session connect to the Bitbucket NFS Server over SSH:

    For Linux or MacOS run following commands in terminal (for Windows use [Git Bash](https://git-scm.com/downloads) terminal):
    
    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NFS_SERVER_IP=nfs_server_private_ip
    export SSH_OPTS1='-o ServerAliveInterval=60'
    export SSH_OPTS2='-o ServerAliveCountMax=30'
    ssh ${SSH_OPTS1} ${SSH_OPTS2} -o "proxycommand ssh -W %h:%p ${SSH_OPTS1} ${SSH_OPTS2} ec2-user@${BASTION_IP}" ec2-user@${NFS_SERVER_IP}
    ```
    For more information, go to [Connecting your nodes over SSH](https://confluence.atlassian.com/adminjiraserver/administering-jira-data-center-on-aws-938846969.html#AdministeringJiraDataCenteronAWS-ConnectingtoyournodesoverSSH).

1. Download the [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/bitbucket/populate_db.sh) script and make it executable:

    ``` bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/bitbucket/populate_db.sh && chmod +x populate_db.sh
    ```
1. Review the following `Variables section` of the script:

    ``` bash
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
    ./populate_db.sh 2>&1 | tee -a populate_db.log
    ```

{{% note %}}
Do not close or interrupt the session. It will take about an hour to restore SQL database. When SQL restoring is finished, an admin user will have `admin`/`admin` credentials.

In case of a failure, check the `Variables` section and run the script one more time.
{{% /note %}}

### <a id="copyingattachments"></a> Restoring attachments (~2 hours)

After [Importing the main dataset](#importingdataset), you'll now have to pre-load an enterprise-scale set of attachments.

{{% note %}}
Populate DB and restore attachments scripts could be run in parallel in separate terminal sessions to save time.
{{% /note %}}

1. Using SSH, connect to the Bitbucket NFS Server via the Bastion instance:

    For Linux or MacOS run following commands in terminal (for Windows use [Git Bash](https://git-scm.com/downloads) terminal):
   
    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NFS_SERVER_IP=nfs_server_private_ip
    export SSH_OPTS1='-o ServerAliveInterval=60'
    export SSH_OPTS2='-o ServerAliveCountMax=30'
    ssh ${SSH_OPTS1} ${SSH_OPTS2} -o "proxycommand ssh -W %h:%p ${SSH_OPTS1} ${SSH_OPTS2} ec2-user@$BASTION_IP" ec2-user@${NFS_SERVER_IP}
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
    ./upload_attachments.sh 2>&1 | tee -a upload_attachments.log
    ```

{{% note %}}
Do not close or interrupt the session. It will take about two hours to upload attachments.
{{% /note %}}


### Start Bitbucket DC
1. Using SSH, connect to the Bitbucket node via the Bastion instance:

    For Linux or MacOS run following commands in terminal (for Windows use [Git Bash](https://git-scm.com/downloads) terminal):
    
    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NODE_IP=node_private_ip
    export SSH_OPTS1='-o ServerAliveInterval=60'
    export SSH_OPTS2='-o ServerAliveCountMax=30'
    ssh ${SSH_OPTS1} ${SSH_OPTS2} -o "proxycommand ssh -W %h:%p ${SSH_OPTS1} ${SSH_OPTS2} ec2-user@${BASTION_IP}" ec2-user@${NODE_IP}
    ```
    For more information, go to [Connecting your nodes over SSH](https://confluence.atlassian.com/adminjiraserver/administering-jira-data-center-on-aws-938846969.html#AdministeringJiraDataCenteronAWS-ConnectingtoyournodesoverSSH).
1. Start Bitbucket DC:

    ``` bash
    sudo systemctl start bitbucket
    ```
1. Wait 10-15 minutes until Bitbucket DC is started.

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

---

### <a id="executionhost"></a>7. Setting up an execution environment

For generating performance results suitable for Marketplace approval process use dedicated execution environment. This is a separate AWS EC2 instance to run the toolkit from. Running the toolkit from a dedicated instance but not from a local machine eliminates network fluctuations and guarantees stable CPU and memory performance.

1. Go to GitHub and create a fork of [dc-app-performance-toolkit](https://github.com/atlassian/dc-app-performance-toolkit).
1. Clone the fork locally, then edit the `bitbucket.yml` configuration file. Set enterprise-scale Bitbucket Data Center parameters:

   ``` yaml
       application_hostname: test_bitbucket_instance.atlassian.com   # Bitbucket DC hostname without protocol and port e.g. test-bitbucket.atlassian.com or localhost
       application_protocol: http      # http or https
       application_port: 80            # 80, 443, 8080, 7990 etc
       secure: True                    # Set False to allow insecure connections, e.g. when using self-signed SSL certificate
       application_postfix:            # e.g. /bitbucket in case of url like http://localhost:7990/bitbucket
       admin_login: admin
       admin_password: admin
       load_executor: jmeter           # only jmeter executor is supported
       concurrency: 20                 # number of concurrent virtual users for jmeter scenario
       test_duration: 50m
       ramp-up: 10m                    # time to spin all concurrent users
       total_actions_per_hour: 32700   # number of total JMeter actions per hour
   ```  

1. Push your changes to the forked repository.
1. [Launch AWS EC2 instance](https://docs.aws.amazon.com/quickstarts/latest/vmlaunch/step-1-launch-instance.html). 
   * OS: select from Quick Start `Ubuntu Server 18.04 LTS`.
   * Instance type: [`c5.2xlarge`](https://aws.amazon.com/ec2/instance-types/c5/)
   * Storage size: `30` GiB
1. Connect to the instance using [SSH](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html) or the [AWS Systems Manager Sessions Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html).

   ```bash
   ssh -i path_to_pem_file ubuntu@INSTANCE_PUBLIC_IP
   ```

1. Install [Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository). Setup manage Docker as a [non-root user](https://docs.docker.com/engine/install/linux-postinstall).
1. Connect to the AWS EC2 instance and clone forked repository.

{{% note %}}
At this stage app-specific actions are not needed yet. Use code from `master` branch with your `bitbucket.yml` changes.
{{% /note %}}

You'll need to run the toolkit for each [test scenario](#testscenario) in the next section.

---

### <a id="testscenario"></a>8. Running the test scenarios on your execution environment

Using the Data Center App Performance Toolkit for [Performance and scale testing your Data Center app](/platform/marketplace/developing-apps-for-atlassian-data-center-products/) involves two test scenarios:

- [Performance regression](#testscenario1)
- [Scalability testing](#testscenario2)

Each scenario will involve multiple test runs. The following subsections explain both in greater detail.

{{% warning %}}
Make sure **English** language is selected as a default language on the **![cog icon](/platform/marketplace/images/cog.png) &gt; Server settings &gt; Language** page. Other languages are **not supported** by the toolkit.
{{% /warning %}}

### <a id="testscenario1"></a> Scenario 1: Performance regression

This scenario helps to identify basic performance issues without a need to spin up a multi-node Bitbucket DC. Make sure the app does not have any performance impact when it is not exercised.

#### <a id="regressionrun1"></a> Run 1 (~1 hour)

To receive performance baseline results **without** an app installed:

1. Use SSH to connect to execution environment.
1. Run toolkit with docker from the execution environment instance:

    ``` bash
    cd dc-app-performance-toolkit
    docker pull atlassian/dcapt
    docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt bitbucket.yml
    ```

1. View the following main results of the run in the `dc-app-performance-toolkit/app/results/bitbucket/YY-MM-DD-hh-mm-ss` folder:
    - `results_summary.log`: detailed run summary
    - `results.csv`: aggregated .csv file with all actions and timings
    - `bzt.log`: logs of the Taurus tool execution
    - `jmeter.*`: logs of the JMeter tool execution
    - `pytest.*`: logs of Pytest-Selenium execution

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps. For an enterprise-scale environment run, the acceptable success rate for actions is 95% and above.
{{% /note %}}


#### <a id="regressionrun2"></a> Run 2 (~1 hour)

To receive performance results with an app installed:

1. Install the app you want to test.
1. Setup app license.
1. Run toolkit with docker from the execution environment instance:

   ``` bash
   cd dc-app-performance-toolkit
   docker pull atlassian/dcapt
   docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt bitbucket.yml
   ```

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps. For an enterprise-scale environment run, the acceptable success rate for actions is 95% and above.
{{% /note %}}



#### Generating a performance regression report

To generate a performance regression report:  

1. Use SSH to connect to execution environment.
1. Install and activate the `virtualenv` as described in `dc-app-performance-toolkit/README.md`
1. Allow current user (for execution environment default user is `ubuntu`) to access Docker generated reports:
   ``` bash
   sudo chown -R ubuntu:ubuntu /home/ubuntu/dc-app-performance-toolkit/app/results
   ```
1. Navigate to the `dc-app-performance-toolkit/app/reports_generation` folder.
1. Edit the `performance_profile.yml` file:
    - Under `runName: "without app"`, in the `fullPath` key, insert the full path to results directory of [Run 1](#regressionrun1).
    - Under `runName: "with app"`, in the `fullPath` key, insert the full path to results directory of [Run 2](#regressionrun2).
1. Run the following command:
    ``` bash
    python csv_chart_generator.py performance_profile.yml
    ```
1. In the `dc-app-performance-toolkit/app/results/reports/YY-MM-DD-hh-mm-ss` folder, view the `.csv` file (with consolidated scenario results), the `.png` chart file and performance scenario summary report.

#### Analyzing report

Use [scp](https://man7.org/linux/man-pages/man1/scp.1.html) command to copy report artifacts from execution env to local drive:

1. From local machine terminal (Git bash terminal for Windows) run command:
   ``` bash
   export EXEC_ENV_PUBLIC_IP=execution_environment_ec2_instance_public_ip
   scp -r -i path_to_exec_env_pem ubuntu@$EXEC_ENV_PUBLIC_IP:/home/ubuntu/dc-app-performance-toolkit/app/results/reports ./reports
   ```
1. Once completed, in the `./reports` folder you will be able to review the action timings with and without your app to see its impact on the performance of the instance. If you see an impact (>20%) on any action timing, we recommend taking a look into the app implementation to understand the root cause of this delta.

### <a id="testscenario2"></a> Scenario 2: Scalability testing

The purpose of scalability testing is to reflect the impact on the customer experience when operating across multiple nodes. For this, you have to run scale testing on your app.

For many apps and extensions to Atlassian products, there should not be a significant performance difference between operating on a single node or across many nodes in Bitbucket DC deployment. To demonstrate performance impacts of operating your app at scale, we recommend testing your Bitbucket DC app in a cluster.

##### <a id="run3"></a> Run 3 (~1 hour)

To receive scalability benchmark results for one-node Bitbucket DC **with** app-specific actions:

1. Apply app-specific code changes to a new branch of forked repo.
1. Use SSH to connect to execution environment.
1. Pull cloned fork repo branch with app-specific actions.
1. Run toolkit with docker from the execution environment instance:

   ``` bash
   cd dc-app-performance-toolkit
   docker pull atlassian/dcapt
   docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt bitbucket.yml
   ```

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps. For an enterprise-scale environment run, the acceptable success rate for actions is 95% and above.
{{% /note %}}



##### <a id="run4"></a> Run 4 (~1 hour)
{{% note %}}
Before scaling your DC make sure that AWS vCPU limit is not lower than needed number. 
Use [vCPU limits calculator](https://aws.amazon.com/premiumsupport/knowledge-center/ec2-on-demand-instance-vcpu-increase/) to see current limit.
The same article has instructions on how to increase limit if needed.
{{% /note %}}

To receive scalability benchmark results for two-node Bitbucket DC with app-specific actions:

1. In the AWS console, go to **CloudFormation > Stack details > Select your stack**.
1. On the **Update** tab, select **Use current template**, and then click **Next**.
1. Enter `2` in the **Maximum number of cluster nodes** and the **Minimum number of cluster nodes** fields.
1. Click **Next > Next > Update stack** and wait until stack is updated.
1. Run toolkit with docker from the execution environment instance:

   ``` bash
   cd dc-app-performance-toolkit
   docker pull atlassian/dcapt
   docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt bitbucket.yml
   ```

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps. For an enterprise-scale environment run, the acceptable success rate for actions is 95% and above.
{{% /note %}}


##### <a id="run5"></a> Run 5 (~1 hour)
{{% note %}}
Before scaling your DC make sure that AWS vCPU limit is not lower than needed number. 
Use [vCPU limits calculator](https://aws.amazon.com/premiumsupport/knowledge-center/ec2-on-demand-instance-vcpu-increase/) to see current limit.
The same article has instructions on how to increase limit if needed.
{{% /note %}}

To receive scalability benchmark results for four-node Bitbucket DC with app-specific actions:

1. Scale your Bitbucket Data Center deployment to 4 nodes the same way as in [Run 4](#run4).
1. Run toolkit with docker from the execution environment instance:

   ``` bash
   cd dc-app-performance-toolkit
   docker pull atlassian/dcapt
   docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt bitbucket.yml
   ```  

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps. For an enterprise-scale environment run, the acceptable success rate for actions is 95% and above.
{{% /note %}}


#### Generating a report for scalability scenario

To generate a scalability report:

1. Use SSH to connect to execution environment.
1. Allow current user (for execution environment default user is `ubuntu`) to access Docker generated reports:
   ``` bash
   sudo chown -R ubuntu:ubuntu /home/ubuntu/dc-app-performance-toolkit/app/results
   ```
1. Navigate to the `dc-app-performance-toolkit/app/reports_generation` folder.
1. Edit the `scale_profile.yml` file:
    - For `runName: "1 Node"`, in the `fullPath` key, insert the full path to results directory of [Run 3](#run3).
    - For `runName: "2 Nodes"`, in the `fullPath` key, insert the full path to results directory of [Run 4](#run4).
    - For `runName: "4 Nodes"`, in the `fullPath` key, insert the full path to results directory of [Run 5](#run5).
1. Run the following command from the `virtualenv` (as described in `dc-app-performance-toolkit/README.md`):
    ``` bash
    python csv_chart_generator.py scale_profile.yml
    ```
1. In the `dc-app-performance-toolkit/app/results/reports/YY-MM-DD-hh-mm-ss` folder, view the `.csv` file (with consolidated scenario results), the `.png` chart file and summary report.


#### Analyzing report

Use [scp](https://man7.org/linux/man-pages/man1/scp.1.html) command to copy report artifacts from execution env to local drive:

1. From local terminal (Git bash terminal for Windows) run command:
   ``` bash
   export EXEC_ENV_PUBLIC_IP=execution_environment_ec2_instance_public_ip
   scp -r -i path_to_exec_env_pem ubuntu@$EXEC_ENV_PUBLIC_IP:/home/ubuntu/dc-app-performance-toolkit/app/results/reports ./reports
   ```
1. Once completed, in the `./reports` folder you will be able to review action timings on Bitbucket Data Center with different numbers of nodes. If you see a significant variation in any action timings between configurations, we recommend taking a look into the app implementation to understand the root cause of this delta.

{{% warning %}}
After completing all your tests, delete your Bitbucket Data Center stacks.
{{% /warning %}}

#### Attaching testing results to DCHELP ticket

{{% warning %}}
Do not forget to attach performance testing results to your DCHELP ticket.
{{% /warning %}}

1. Make sure you have two reports folders: one with performance profile and second with scale profile results. 
   Each folder should have `profile.csv`, `profile.png`, `profile_summary.log` and profile run result archives.
1. Attach two reports folders to your DCHELP ticket.


## Support
In case of technical questions, issues or problems with DC Apps Performance Toolkit, contact us for support in the [community Slack](http://bit.ly/dcapt_slack) **#data-center-app-performance-toolkit** channel.
