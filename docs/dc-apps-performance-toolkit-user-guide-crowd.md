---
title: "Data Center App Performance Toolkit User Guide For Crowd"
platform: platform
product: marketplace
category: devguide
subcategory: build
date: "2022-02-13"
---
# Data Center App Performance Toolkit User Guide For Crowd

This document walks you through the process of testing your app on Crowd using the Data Center App Performance Toolkit. These instructions focus on producing the required [performance and scale benchmarks for your Data Center app](/platform/marketplace/dc-apps-performance-and-scale-testing/).

In this document, we cover the use of the Data Center App Performance Toolkit on Enterprise-scale environment.

**Enterprise-scale environment**: Crowd Data Center environment used to generate Data Center App Performance Toolkit test results for the Marketplace approval process. Preferably, use the [AWS Quick Start for Crowd Data Center](https://aws.amazon.com/quickstart/architecture/atlassian-crowd) with the parameters prescribed below. These parameters provision larger, more powerful infrastructure for your Crowd Data Center.

1. [Set up an enterprise-scale environment Crowd Data Center on AWS](#instancesetup).
2. [Load an enterprise-scale dataset on your Crowd Data Center deployment](#preloading).
3. [App-specific actions development](#appspecificaction).   
4. [Set up an execution environment for the toolkit](#executionhost).
5. [Running the test scenarios from execution environment against enterprise-scale Crowd Data Center](#testscenario).

---

## <a id="instancesetup"></a>1. Set up an enterprise-scale environment Crowd Data Center on AWS

We recommend that you use the [AWS Quick Start for Crowd Data Center](https://aws.amazon.com/quickstart/architecture/atlassian-crowd) (**How to deploy** tab) to deploy a Crowd Data Center enterprise-scale environment. This Quick Start will allow you to deploy Crowd Data Center with a new [Atlassian Standard Infrastructure](https://aws.amazon.com/quickstart/architecture/atlassian-standard-infrastructure/) (ASI) or into an existing one.

The ASI is a Virtual Private Cloud (VPC) consisting of subnets, NAT gateways, security groups, bastion hosts, and other infrastructure components required by all Atlassian applications, and then deploys Crowd into this new VPC. Deploying Crowd with a new ASI takes around 50 minutes. With an existing one, it'll take around 30 minutes.

#### Using the AWS Quick Start for Crowd

If you are a new user, perform an end-to-end deployment. This involves deploying Crowd into a _new_ ASI:

Navigate to **[AWS Quick Start for Crowd Data Center](https://aws.amazon.com/quickstart/architecture/atlassian-crowd/) &gt; How to deploy** tab **&gt; Deploy into a new ASI** link.

If you have already deployed the ASI separately by using the [ASI Quick Start](https://aws.amazon.com/quickstart/architecture/atlassian-standard-infrastructure/)ASI Quick Start or by deploying another Atlassian product (Jira, Bitbucket, Confluence or Crowd Data Center development environment) with ASI, deploy Crowd into your existing ASI:

Navigate to **[AWS Quick Start for Crowd Data Center](https://aws.amazon.com/quickstart/architecture/atlassian-crowd) &gt; How to deploy** tab **&gt; Deploy into your existing ASI** link.

{{% note %}}
You are responsible for the cost of the AWS services used while running this Quick Start reference deployment. There is no additional price for using this Quick Start. For more information, go to [aws.amazon.com/pricing](https://aws.amazon.com/ec2/pricing/).
{{% /note %}}

To reduce costs, we recommend you to keep your deployment up and running only during the performance runs.

#### AWS cost estimation
[AWS Pricing Calculator](https://calculator.aws/) provides an estimate of usage charges for AWS services based on certain information you provide.
Monthly charges will be based on your actual usage of AWS services and may vary from the estimates the Calculator has provided.

*The prices below are approximate and may vary depending on such factors like region, instance type, deployment type of DB, and other.  


| Stack | Estimated hourly cost ($) |
| ----- | ------------------------- |
| One Node Crowd DC | 0.4 - 0.6
| Two Nodes Crowd DC | 0.6 - 0.8
| Four Nodes Crowd DC | 0.9 - 1.4

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

#### <a id="quick-start-parameters"></a> Quick Start parameters

All important parameters are listed and described in this section. For all other remaining parameters, we recommend using the Quick Start defaults.

**Crowd setup**

| Parameter | Recommended Value                                                   |
| --------- |---------------------------------------------------------------------|
| Version | The Data Center App Performance Toolkit officially supports `5.0.2` |

**Cluster nodes**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Cluster node instance type | [c5.xlarge](https://aws.amazon.com/ec2/instance-types/c5/)
| Maximum number of cluster nodes | 1 |
| Minimum number of cluster nodes | 1 |
| Cluster node instance volume size | 100 |

**Database**

| Parameter | Recommended Value |
| --------- | ----------------- |
| The database engine to deploy with | PostgresSQL |
| The database engine version to use | 11 |
| Database instance class | [db.m5.large](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html#Concepts.DBInstanceClass.Summary) |
| RDS Provisioned IOPS | 1000 |
| Master (admin) password | Password1! |
| Enable RDS Multi-AZ deployment | false |
| Application user database password | Password1! |
| Database storage | 200 |

{{% note %}}
The **Master (admin) password** will be used later when restoring the SQL database dataset. If password value is not set to default, you'll need to change `DB_PASS` value manually in the restore database dump script (later in [Preloading your Crowd deployment with an enterprise-scale dataset](#preloading)).
{{% /note %}}

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

#### Running the setup wizard

After successfully deploying Crowd Data Center in AWS, you'll need to configure it:

1. In the AWS console, go to **Services** > **CloudFormation** > **Stack** > **Stack details** > **Select your stack**.
1. On the **Outputs** tab, copy the value of the **LoadBalancerURL** key.
1. Open **LoadBalancerURL** in your browser. This will take you to the Crowd setup wizard.
1. On the **License** page, populate the **License Key** field by either:
    - Using your existing license, or
    - Generating a Crowd trial license, or
    - Contacting Atlassian to be provided two time-bomb licenses for testing.  
    Click **Continue**.
1. On the **Crowd installation** page choose **New Installation** and click **Continue**.
1. On the **Database configuration** page, leave all fields default and click **Continue**.
1. On the **Options** page, populate the following fields:
    - **Deployment title**: any instance title
    - **Session timeout**: 30 _(recommended)_. The number of minutes a session lasts before expiring. Must be greater than 0.
    - **Base Url**: review and confirm the Crowd instance base url.  
    Click **Continue**.
1. On the **Internal directory** page, populate the following fields and press **Continue**:
    - **Name**: a short, recognisable name that characterises this user directory.
    - **Password encryption**: chose **ATLASSIAN-SECURITY** from the dropdown list _(recommended)_  
   Click **Continue**.
1. On the **Default administrator** page, fill the following fields:
    - **Email Address**: email address of the admin user
    - **Username**: admin _(recommended)_
    - **Password**: admin _(recommended)_
    - **Confirm Password**: admin _(recommended)_
    - **First name**: admin user first name
    - **Last name**: admin user last name  
   Click **Continue**.
1. On the **Integrated applications** page leave **Open ID server** unchecked and click **Continue**.

---

## <a id="preloading"></a>2. Preloading your Crowd deployment with an enterprise-scale dataset

Data dimensions and values for an enterprise-scale dataset are listed and described in the following table.

| Data dimensions | Value for an enterprise-scale dataset |
| --------------- | ------------------------------------- |
| Users | ~100 000 |
| Groups | ~15 |

{{% note %}}
All the datasets use the standard `admin`/`admin` credentials.
{{% /note %}}

#### Pre-loading the dataset:

[Importing the main dataset](#importingdataset). To help you out, we provide an enterprise-scale dataset you can import either via the [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/crowd/populate_db.sh) script or restore from xml backup file.

The following subsections explain dataset import process in greater detail.

#### <a id="importingdataset"></a> Importing the main dataset

You can load this dataset directly into the database (via a [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/crowd/populate_db.sh) script), or import it via XML.  

##### Option 1 (recommended): Loading the dataset via populate_db.sh script (~15 minutes)


To populate the database with SQL:

1. In the AWS console, go to **Services** > **EC2** > **Instances**.
1. On the **Description** tab, do the following:
    - Copy the _Public IP_ of the Bastion instance.
    - Copy the _Private IP_ of the Crowd node instance.
1. Using SSH, connect to the Crowd node via the Bastion instance:

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
1. Download the [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/crowd/populate_db.sh) script and make it executable:

    ``` bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/crowd/populate_db.sh && chmod +x populate_db.sh
    ```
1. Review the following `Variables section` of the script:

    ``` bash
    DB_CONFIG="/usr/lib/systemd/system/crowd.service"
    CROWD_DB_NAME="crowd"
    CROWD_DB_USER="postgres"
    CROWD_DB_PASSWORD="Password1!"
    ```
1. Run the script:

    ``` bash
    ./populate_db.sh 2>&1 | tee -a populate_db.log
    ```

{{% note %}}
Do not close or interrupt the session. It will take about an hour to restore SQL database. When SQL restoring is finished, an admin user will have `admin`/`admin` credentials.

In case of a failure, check the `Variables` section and run the script one more time.
{{% /note %}}

##### Option 2: Loading the dataset through XML import (~30 minutes)

We recommend that you only use this method if you are having problems with the [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/crowd/populate_db.sh) script.

1. In the AWS console, go to **Services** > **EC2** > **Instances**.
1. On the **Description** tab, do the following:
    - Copy the _Public IP_ of the Bastion instance.
    - Copy the _Private IP_ of the Crowd node instance.
1. Using SSH, connect to the Crowd node via the Bastion instance:

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
1. Download the db.xml file corresponding to your Crowd version.

    ``` bash
    CROWD_VERSION=$(sudo su crowd -c "cat /media/atl/crowd/shared/crowd.version")
    sudo su crowd -c "wget https://centaurus-datasets.s3.amazonaws.com/crowd/${CROWD_VERSION}/large/db.xml -O /media/atl/crowd/shared/db.xml"
    ```
1. Log in as a user with the **Crowd System Administrators** [global permission](https://confluence.atlassian.com/adminjiraserver/managing-global-permissions-938847142.html).
1. Go to **![cog icon](/platform/marketplace/images/cog.png) &gt; Restore.** from the menu.
1. Populate the **Restore file path** field with `/media/atl/crowd/shared/db.xml`.
1. Click **Submit** and wait until the import is completed.

---
{{% note %}}
After [Preloading your Crowd deployment with an enterprise-scale dataset](#preloading), the admin user will have `admin`/`admin` credentials.
It's recommended to change default password from UI account page for security reasons.
{{% /note %}}
---

## <a id="appspecificaction"></a>3. App-specific actions development

Data Center App Performance Toolkit has its own set of default [JMeter](https://jmeter.apache.org/) test actions for Crowd Data Center.

**App-specific action** - action (performance test) you have to develop to cover main use cases of your application. Performance test should focus on the common usage of your application and not to cover all possible functionality of your app. For example, application setup screen or other one-time use cases are out of scope of performance testing.

**JMeter app-specific actions development**

1. Set up local environment for toolkit using the [README](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/README.md).
1. Check that `crowd.yml` file has correct settings of `application_hostname`, `application_protocol`, `application_port`, `application_postfix`, etc.
1. Navigate to `dc-app-performance-toolkit/app` folder and run from virtualenv(as described in `dc-app-performance-toolkit/README.md`):
    
    ```python util/jmeter/start_jmeter_ui.py --app crowd```
1. Open `Crowd` thread group and add new transaction controller.
1. Open newly added transaction controller, and add new HTTP requests (based on your app use cases) into it.
1. Run toolkit locally from `dc-app-performance-toolkit/app` folder with the command  
```bzt crowd.yml```  
   Make sure that execution is successful.

---

## <a id="executionhost"></a>4. Setting up an execution environment

For generating performance results suitable for Marketplace approval process use dedicated execution environment. This is a separate AWS EC2 instance to run the toolkit from. Running the toolkit from a dedicated instance but not from a local machine eliminates network fluctuations and guarantees stable CPU and memory performance.

1. Go to GitHub and create a fork of [dc-app-performance-toolkit](https://github.com/atlassian/dc-app-performance-toolkit).
1. Clone the fork locally, then edit the `crowd.yml` configuration file. Set enterprise-scale Crowd Data Center parameters:

{{% warning %}}
Do not push to the fork real `application_hostname`, `admin_login` and `admin_password` values for security reasons.
Instead, set those values directly in `.yml` file on execution environment instance.
{{% /warning %}}

   ``` yaml
    application_hostname: test_crowd_instance.atlassian.com    # Crowd DC hostname without protocol and port e.g. test-crowd.atlassian.com or localhost
    application_protocol: http      # http or https
    application_port: 80            # 80, 443, 8080, 4990, etc
    secure: True                    # Set False to allow insecure connections, e.g. when using self-signed SSL certificate
    application_postfix:            # e.g. /crowd in case of url like http://localhost:4990/crowd
    admin_login: admin
    admin_password: admin
    application_name: crowd
    application_password: 1111
    load_executor: jmeter            
    concurrency: 1000               # number of concurrent threads to authenticate random users
    test_duration: 45m
   ```  

1. Push your changes to the forked repository.
1. [Launch AWS EC2 instance](https://console.aws.amazon.com/ec2/). 
   * OS: select from Quick Start `Ubuntu Server 20.04 LTS`.
   * Instance type: [`c5.2xlarge`](https://aws.amazon.com/ec2/instance-types/c5/)
   * Storage size: `30` GiB
1. Connect to the instance using [SSH](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html) or the [AWS Systems Manager Sessions Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html).

   ```bash
   ssh -i path_to_pem_file ubuntu@INSTANCE_PUBLIC_IP
   ```

1. Install [Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository). Setup manage Docker as a [non-root user](https://docs.docker.com/engine/install/linux-postinstall).
1. Clone forked repository.


You'll need to run the toolkit for each [test scenario](#testscenario) in the next section.

---

## <a id="testscenario"></a>5. Running the test scenarios from execution environment against enterprise-scale Crowd Data Center

Using the Data Center App Performance Toolkit for [Performance and scale testing your Data Center app](/platform/marketplace/developing-apps-for-atlassian-data-center-products/) involves two test scenarios:

- [Performance regression](#testscenario1)
- [Scalability testing](#testscenario2)

Each scenario will involve multiple test runs. The following subsections explain both in greater detail.

#### <a id="testscenario1"></a> Scenario 1: Performance regression

This scenario helps to identify basic performance issues without a need to spin up a multi-node Crowd DC. Make sure the app does not have any performance impact when it is not exercised.

##### <a id="regressionrun1"></a> Run 1 (~50 min)

To receive performance baseline results **without** an app installed and **without** app-specific actions (use code from `master` branch):

1. Use SSH to connect to execution environment.
1. Run toolkit with docker from the execution environment instance:

    ``` bash
    cd dc-app-performance-toolkit
    docker pull atlassian/dcapt
    docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt crowd.yml
    ```

1. View the following main results of the run in the `dc-app-performance-toolkit/app/results/crowd/YY-MM-DD-hh-mm-ss` folder:
    - `results_summary.log`: detailed run summary
    - `results.csv`: aggregated .csv file with all actions and timings
    - `bzt.log`: logs of the Taurus tool execution
    - `jmeter.*`: logs of the JMeter tool execution

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps. For an enterprise-scale environment run, the acceptable success rate for actions is 95% and above.
{{% /note %}}

##### <a id="regressionrun2"></a> Run 2


**Performance results generation with the app installed (still use master branch):**

1. Run toolkit with docker from the execution environment instance:

   ``` bash
   cd dc-app-performance-toolkit
   docker pull atlassian/dcapt
   docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt crowd.yml
   ```

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps. For an enterprise-scale environment run, the acceptable success rate for actions is 95% and above.
{{% /note %}}


##### Generating a performance regression report

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


#### <a id="testscenario2"></a> Scenario 2: Scalability testing

The purpose of scalability testing is to reflect the impact on the customer experience when operating across multiple nodes. For this, you have to run scale testing on your app.

For many apps and extensions to Atlassian products, there should not be a significant performance difference between operating on a single node or across many nodes in Crowd DC deployment. To demonstrate performance impacts of operating your app at scale, we recommend testing your Crowd DC app in a cluster.


###### <a id="run3"></a> Run 3 (~50 min)

To receive scalability benchmark results for one-node Crowd DC **with** app-specific actions:

1. Apply app-specific code changes to a new branch of forked repo.
1. Use SSH to connect to execution environment.
1. Pull cloned fork repo branch with app-specific actions.
1. Run toolkit with docker from the execution environment instance:

   ``` bash
   cd dc-app-performance-toolkit
   docker pull atlassian/dcapt
   docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt crowd.yml
   ```

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps. For an enterprise-scale environment run, the acceptable success rate for actions is 95% and above.
{{% /note %}}


##### <a id="run4"></a> Run 4 (~50 min)
{{% note %}}
Before scaling your DC make sure that AWS vCPU limit is not lower than needed number. 
Use [vCPU limits calculator](https://aws.amazon.com/premiumsupport/knowledge-center/ec2-on-demand-instance-vcpu-increase/) to see current limit.
The same article has instructions on how to increase limit if needed.
{{% /note %}}

To receive scalability benchmark results for two-node Crowd DC **with** app-specific actions:

1. In the AWS console, go to **CloudFormation** > **Stack details** > **Select your stack**.
2. On the **Update** tab, select **Use current template**, and then click **Next**.
3. Enter `2` in the **Maximum number of cluster nodes** and the **Minimum number of cluster nodes** fields.
4. Click **Next** > **Next** > **Update stack** and wait until stack is updated.

{{% warning %}}
In case if you got error during update - `BastionPrivIp cannot be updated`.
Please use those steps for a workaround:
1. In the AWS console, go to **EC2** > **Auto Scailng** > **Auto Scaling Groups**.
2. On the **Auto Scaling Groups** page, select **your stack ASG** and click **Edit**
3. Enter `2` in the **Desired capacity**, **Minimum capacity** and **Maximum capacity** fields.
4. Scroll down, click **Update** button and wait until stack is updated. 
{{% /warning %}}

5. Edit **run parameters** for 2 nodes run. To do it, left uncommented only 2 nodes scenario parameters in `crowd.yml` file.
   ```
   # 1 node scenario parameters
   # ramp-up: 20s                    # time to spin all concurrent threads
   # total_actions_per_hour: 180000  # number of total JMeter actions per hour

   # 2 nodes scenario parameters
     ramp-up: 10s                    # time to spin all concurrent threads
     total_actions_per_hour: 360000  # number of total JMeter actions per hour

   # 4 nodes scenario parameters
   # ramp-up: 5s                     # time to spin all concurrent threads
   # total_actions_per_hour: 720000  # number of total JMeter actions per hour
   ```
6. Run toolkit with docker from the execution environment instance:

   ``` bash
   cd dc-app-performance-toolkit
   docker pull atlassian/dcapt
   docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt crowd.yml
   ```

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps. For an enterprise-scale environment run, the acceptable success rate for actions is 95% and above.
{{% /note %}}


##### <a id="run5"></a> Run 5 (~50 min)
{{% note %}}
Before scaling your DC make sure that AWS vCPU limit is not lower than needed number. 
Use [vCPU limits calculator](https://aws.amazon.com/premiumsupport/knowledge-center/ec2-on-demand-instance-vcpu-increase/) to see current limit.
The same article has instructions on how to increase limit if needed.
{{% /note %}}

To receive scalability benchmark results for four-node Crowd DC with app-specific actions:

1. Scale your Crowd Data Center deployment to 4 nodes as described in [Run 4](#run4).
1. Edit **run parameters** for 4 nodes run. To do it, left uncommented only 4 nodes scenario parameters `crowd.yml` file.
   ```
   # 1 node scenario parameters
   # ramp-up: 20s                    # time to spin all concurrent threads
   # total_actions_per_hour: 180000  # number of total JMeter actions per hour

   # 2 nodes scenario parameters
   # ramp-up: 10s                    # time to spin all concurrent threads
   # total_actions_per_hour: 360000  # number of total JMeter actions per hour

   # 4 nodes scenario parameters
   ramp-up: 5s                     # time to spin all concurrent threads
   total_actions_per_hour: 720000  # number of total JMeter actions per hour
   ```   
   
1. Run toolkit with docker from the execution environment instance:

   ``` bash
   cd dc-app-performance-toolkit
   docker pull atlassian/dcapt
   docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt crowd.yml
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
    - For `runName: "Node 1"`, in the `fullPath` key, insert the full path to results directory of [Run 3](#run3).
    - For `runName: "Node 2"`, in the `fullPath` key, insert the full path to results directory of [Run 4](#run4).
    - For `runName: "Node 4"`, in the `fullPath` key, insert the full path to results directory of [Run 5](#run5).
1. Run the following command from the activated `virtualenv` (as described in `dc-app-performance-toolkit/README.md`):
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
1. Once completed, in the `./reports` folder you will be able to review action timings on Crowd Data Center with different numbers of nodes. If you see a significant variation in any action timings between configurations, we recommend taking a look into the app implementation to understand the root cause of this delta.

{{% warning %}}
After completing all your tests, delete your Crowd Data Center stacks.
{{% /warning %}}

#### Attaching testing results to ECOHELP ticket

{{% warning %}}
Do not forget to attach performance testing results to your ECOHELP ticket.
{{% /warning %}}

1. Make sure you have two reports folders: one with performance profile and second with scale profile results. 
   Each folder should have `profile.csv`, `profile.png`, `profile_summary.log` and profile run result archives. Archives 
   should contain all raw data created during the run: `bzt.log`, selenium/jmeter/locust logs, .csv and .yml files, etc.
2. Attach two reports folders to your ECOHELP ticket.

## <a id="support"></a> Support
In case of technical questions, issues or problems with DC Apps Performance Toolkit, contact us for support in the [community Slack](http://bit.ly/dcapt_slack) **#data-center-app-performance-toolkit** channel.
