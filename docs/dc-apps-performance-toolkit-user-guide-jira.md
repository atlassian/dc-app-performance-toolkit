---
title: "Data Center App Performance Toolkit User Guide For Jira"
platform: platform
product: marketplace
category: devguide
subcategory: build
date: "2019-09-12"
---
# Data Center App Performance Toolkit User Guide For Jira

To use the Data Center App Performance Toolkit, you'll need to first clone its repo.

``` bash
git clone git@github.com:atlassian/dc-app-performance-toolkit.git
```

Follow installation instructions described in the `dc-app-performance-toolkit/README.md` file.

If you need performance testing results at a production level, follow instructions in this chapter to set up Jira Data Center with the corresponding dataset.

For spiking, testing, or developing, your local Jira instance would work well. Thus, you can skip this chapter and proceed with [Testing scenarios](/platform/marketplace/dc-apps-performance-toolkit-user-guide-jira/#testing-scenarios). Still, script adjustments for your local dataset may be required.

## Setting up Jira Data Center

We recommend that you use the [AWS Quick Start for Jira Data Center](https://aws.amazon.com/quickstart/architecture/jira/) to deploy a Jira Data Center testing environment. This Quick Start will allow you to deploy Jira Data Center with a new [Atlassian Standard Infrastructure](https://aws.amazon.com/quickstart/architecture/atlassian-standard-infrastructure/) (ASI) or into an existing one.

The ASI is a Virtual Private Cloud (VPC) consisting of subnets, NAT gateways, security groups, bastion hosts, and other infrastructure components required by all Atlassian applications, and then deploys Jira into this new VPC. Deploying Jira with a new ASI takes around 50 minutes. With an existing one, it'll take around 30 minutes.

### Using the AWS Quick Start for Jira

If you are a new user, perform an end-to-end deployment. This involves deploying Jira into a _new_ ASI.

If you have already deployed the ASI separately by using the [ASI Quick Start](https://aws.amazon.com/quickstart/architecture/atlassian-standard-infrastructure/)ASI Quick Start or by deploying another Atlassian product (Jira, Bitbucket, or Confluence Data Center), deploy Jira into your existing ASI.

{{% note %}}
You are responsible for the cost of the AWS services used while running this Quick Start reference deployment. There is no additional price for using this Quick Start. For more information, go to [aws.amazon.com/pricing](https://aws.amazon.com/ec2/pricing/).
{{% /note %}}

To reduce costs, we recommend you to keep your deployment up and running only during the performance runs.

### AWS cost estimation ###
[SIMPLE MONTHLY CALCULATOR](https://calculator.s3.amazonaws.com/index.html) provides an estimate of usage charges for AWS services based on certain information you provide.
Monthly charges will be based on your actual usage of AWS services, and may vary from the estimates the Calculator has provided.

*The prices below are approximate and may vary depending on factors such as (region, instance type, deployment type of DB, etc.)

| Stack | Estimated hourly cost ($) |
| ----- | ------------------------- |
| One Node Jira DC | 1 - 1.3 |
| Two Nodes Jira DC  1.7 - 2.1 |
| Four Nodes Jira DC | 3.1 - 3.8 |

#### Quick Start parameters

All important parameters are listed and described in this section. For all other remaining parameters, we recommend using the Quick Start defaults.

**Jira setup**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Jira Product | Software |
| Jira Version | 8.0.3 or 7.13.6 or 8.5.0 |

The Data Center App Performance Toolkit officially supports:

- The latest Jira Platform Release version: 8.0.3
- The following Jira [Enterprise Releases](https://confluence.atlassian.com/enterprise/atlassian-enterprise-releases-948227420.html): 7.13.6 and 8.5.0

**Cluster nodes**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Cluster node instance type | [c5.4xlarge](https://aws.amazon.com/ec2/instance-types/c5/) |
| Maximum number of cluster nodes | 1 |
| Minimum number of cluster nodes | 1 |
| Cluster node instance volume size | 100 |

We recommend [c5.4xlarge](https://aws.amazon.com/ec2/instance-types/c5/) to strike the balance between cost and hardware we see in the field for our enterprise customers. This differs from our [public recommendation on c4.8xlarge](https://confluence.atlassian.com/enterprise/infrastructure-recommendations-for-enterprise-jira-instances-on-aws-969532459.html) for production instances but is representative for a lot of our Jira Data Center customers.

The Data Center App Performance Toolkit framework is also set up for concurrency we expect on this instance size. As such, underprovisioning will likely show a larger performance impact than expected.

**Database**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Database instance class | [db.m5.large](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html#Concepts.DBInstanceClass.Summary) |
| RDS Provisioned IOPS | 1000 |
| Master (admin) password | Password1! |
| Enable RDS Multi-AZ deployment | true |
| Application user database password | Password1! |

{{% note %}}
The **Master (admin) password** will be used later when restoring the SQL database dataset. If password value is not set to default, you'll need to change `DB_PASS` value manually in the restore database dump script (later in [Preloading your Jira deployment with an enterprise-scale dataset](#preloading)).
{{% /note %}}

**Networking (for new ASI)**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Trusted IP range | 0.0.0.0/0 _(for public access) or your own trusted IP range_ |
| Availability Zones | _Select two availability zones in your region. Both zones must support EFS (see [Supported AWS regions](https://confluence.atlassian.com/enterprise/getting-started-with-jira-data-center-on-aws-969535550.html#GettingstartedwithJiraDataCenteronAWS-SupportedAWSregions) for details)._ |
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

After successfully deploying Jira Data Center in AWS, you'll need to configure it:

1. In the AWS console, go to **Services > CloudFormation > Stack > Stack details > Select your stack**.
1. On the **Outputs** tab, copy the value of the **LoadBalancerURL** key.
1. Open **LoadBalancerURL** in your browser. This will take you to the Jira setup wizard.
1. On the **Set up application properties** page, populate the following fields:
    - **Application Title**: any name for your Jira Data Center deployment
    - **Mode**: Private
    - **Base URL**: your stack's Elastic LoadBalancer URL
    Click **Next**.
1. On the next page, populate the **Your License Key** field by either:
    - Using your existing license, or
    - Generating a Jira trial license, or
    - Contacting Atlassian to be provided two time-bomb licenses for testing. Ask for it in your DCHELP ticket.
    Click **Next**.
1. On the **Set up administrator account** page, populate the following fields:
    - **Full name**: any full name of the admin user
    - **Email Address**: email address of the admin user
    - **Username**: admin _(recommended)_
    - **Password**: admin _(recommended)_
    - **Confirm Password**: admin _(recommended)_
    Click **Next**.
1. On the **Set up email notifications** page, configure your email notifications, and then click **Finish**.
1. After going through the welcome setup, click **Create new project** to create a new project.

{{% note %}}
After [Preloading your Jira deployment with an enterprise-scale dataset](#preloading), the admin user will have `admin`/`admin` credentials.
{{% /note %}}

## <a id="preloading"></a> Preloading your Jira deployment with an enterprise-scale dataset

Data dimensions and values for an enterprise-scale dataset are listed and described in the following table.

| Data dimensions | Value for an enterprise-scale dataset |
| --------------- | ------------------------------------- |
| Attachments | ~2 000 000 |
| Comments | ~6 000 000 |
| Components  | ~2 500 |
| Custom fields | ~800 |
| Groups | ~1 000 |
| Issue security levels | 10 |
| Issue types | ~300 |
| Issues | ~1 000 000 |
| Priorities | 5 |
| Projects | 500 |
| Resolutions | 34 |
| Screen schemes | ~200 |
| Screens | ~200 |
| Statuses | ~400 |
| Users | ~21 000 |
| Versions | ~20 000 |
| Workflows | 50 |

{{% note %}}
All the datasets use the standard `admin`/`admin` credentials.
{{% /note %}}

Pre-loading the dataset is a three-step process:

1. [Importing the main dataset](#importingdataset). To help you out, we provide an enterprise-scale dataset you can import either via the [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/populate_db.sh) script or restore from xml backup file.
1. [Restoring attachments](#copyingattachments). We also provide attachments, which you can pre-load via an [upload_attachments.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/upload_attachments.sh) script.
1. [Re-indexing Jira Data Center](#reindexing). For more information, go to [Re-indexing Jira](https://confluence.atlassian.com/adminjiraserver/search-indexing-938847710.html).

The following subsections explain each step in greater detail.

### <a id="importingdataset"></a> Importing the main dataset

You can load this dataset directly into the database (via a [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/populate_db.sh) script), or import it via XML.  

#### Option 1: Loading the dataset via populate_db.sh script (~1 hour)

{{% note %}}
We recommend doing this via the CLI.
{{% /note %}}

To populate the database with SQL:

1. In the AWS console, go to **Services > EC2 > Instances**.
1. On the **Description** tab, do the following:
    - Copy the _Public IP_ of the Bastion instance.
    - Copy the _Private IP_ of Jira node instance.
1. Using SSH, connect to the Jira node via the Bastion instance:

    For Windows, use Putty to connect to the Jira node over SSH.
    For Linux or MacOS:
    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NODE_IP=node_private_ip
    export SSH_OPTS='-o ServerAliveInterval=60 -o ServerAliveCountMax=30'
    ssh ${SSH_OPTS} -o "proxycommand ssh -W %h:%p ${SSH_OPTS} ec2-user@${BASTION_IP}" ec2-user@${NODE_IP}
    ```
    For more information, go to [Connecting your nodes over SSH](https://confluence.atlassian.com/adminjiraserver/administering-jira-data-center-on-aws-938846969.html#AdministeringJiraDataCenteronAWS-ConnectingtoyournodesoverSSH).
1. Download the [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/populate_db.sh) script and make it executable:

    ``` bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/jira/populate_db.sh && chmod +x populate_db.sh
    ```
1. Review the following `Variables section` of the script:

    ``` bash
    INSTALL_PSQL_CMD="amazon-linux-extras install -y postgresql10"
    DB_CONFIG="/var/atlassian/application-data/jira/dbconfig.xml"
    JIRA_CURRENT_DIR="/opt/atlassian/jira-software/current"
    CATALINA_PID_FILE="${JIRA_CURRENT_DIR}/work/catalina.pid"
    JIRA_DB_NAME="jira"
    JIRA_DB_USER="postgres"
    JIRA_DB_PASS="Password1!"
    JIRA_SETENV_FILE="${JIRA_CURRENT_DIR}/bin/setenv.sh"
    JIRA_VERSION_FILE="/media/atl/jira/shared/jira-software.version"
    DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/jira"
    ```
1. Run the script:

    ``` bash
    ./populate_db.sh | tee -a populate_db.log
    ```

{{% note %}}
Do not close or interrupt the session. It will take about an hour to restore SQL database. When SQL restoring is finished, an admin user will have `admin`/`admin` credentials.

In case of a failure, check the `Variables` section and run the script one more time.
{{% /note %}}

#### Option 2: Loading the dataset through XML import (~4 hours)

We recommend that you only use this method if you are having problems with the [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/populate_db.sh) script.

1. In the AWS console, go to **Services > EC2 > Instances**.
1. On the **Description** tab, do the following:
    - Copy the _Public IP_ of the Bastion instance.
    - Copy the _Private IP_ Jira node instance.
1. Using SSH, connect to the Jira node via the Bastion instance:

    For Windows, use Putty to connect to the Jira node over SSH.
    For Linux or MacOS:
    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NODE_IP=node_private_ip
    export SSH_OPTS='-o ServerAliveInterval=60 -o ServerAliveCountMax=30'
    ssh ${SSH_OPTS} -o "proxycommand ssh -W %h:%p ${SSH_OPTS} ec2-user@${BASTION_IP}" ec2-user@${NODE_IP}
    ```
    For more information, go to [Connecting your nodes over SSH](https://confluence.atlassian.com/adminjiraserver/administering-jira-data-center-on-aws-938846969.html#AdministeringJiraDataCenteronAWS-ConnectingtoyournodesoverSSH).
1. Download the xml_backup.zip file corresponding to your Jira version.

    ``` bash
    JIRA_VERSION=$(sudo su jira -c "cat /media/atl/jira/shared/jira-software.version")
    sudo su jira -c "wget https://centaurus-datasets.s3.amazonaws.com/jira/${JIRA_VERSION}/large/xml_backup.zip -O /media/atl/jira/shared/import/xml_backup.zip"
    ```
1. From a different computer, log in as a user with the **Jira System Administrators** [global permission](https://confluence.atlassian.com/adminjiraserver/managing-global-permissions-938847142.html).
1. Go to **![cog icon](/platform/marketplace/images/cog.png) &gt; System &gt; Restore System.** from the menu.
1. Populate the **File name** field with `xml_backup.zip`.
1. Click **Restore** and wait until the import is completed.

### <a id="copyingattachments"></a> Restoring attachments (~2 hours)

After [Importing the main dataset](#importingdataset), you'll now have to pre-load an enterprise-scale set of attachments.

1. Using SSH, connect to the Jira node via the Bastion instance:

    For Windows, use Putty to connect to the Jira node over SSH.
    For Linux or MacOS:
    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NODE_IP=node_private_ip
    export SSH_OPTS='-o ServerAliveInterval=60 -o ServerAliveCountMax=30'
    ssh ${SSH_OPTS} -o "proxycommand ssh -W %h:%p ${SSH_OPTS} ec2-user@$BASTION_IP" ec2-user@${NODE_IP}
    ```
    For more information, go to [Connecting your nodes over SSH](https://confluence.atlassian.com/adminjiraserver/administering-jira-data-center-on-aws-938846969.html#AdministeringJiraDataCenteronAWS-ConnectingtoyournodesoverSSH).
1. Download the [upload_attachments.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/upload_attachments.sh) script and make it executable:

    ``` bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/jira/upload_attachments.sh && chmod +x upload_attachments.sh
    ```    
1. Review the following `Variables section` of the script:

    ``` bash
    DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/jira"
    ATTACHMENTS_TAR="attachments.tar.gz"
    ATTACHMENTS_DIR="attachments"
    TMP_DIR="/tmp"
    EFS_DIR="/media/atl/jira/shared/data"
    ```
1. Run the script:

    ``` bash
    ./upload_attachments.sh | tee -a upload_attachments.log
    ```

{{% note %}}
Do not close or interrupt the session. It will take about two hours to upload attachments to Elastic File Storage (EFS).
{{% /note %}}

### <a id="reindexing"></a> Re-indexing Jira Data Center (~1 hour)

For more information, go to [Re-indexing Jira](https://confluence.atlassian.com/adminjiraserver/search-indexing-938847710.html).

1. Log in as a user with the **Jira System Administrators** [global permission](https://confluence.atlassian.com/adminjiraserver/managing-global-permissions-938847142.html).
1. Go to **![cog icon](/platform/marketplace/images/cog.png) &gt; System &gt; Indexing**.
1. Select the **Lock one Jira node and rebuild index** option.
1. Click **Re-Index** and wait until re-indexing is completed.

Jira will be unavailable for some time during the re-indexing process. When finished, the **Acknowledge** button will be available on the re-indexing page.

{{% note %}}
Go to **![cog icon](/platform/marketplace/images/cog.png) &gt; System &gt; General configuration**, click **Edit Settings** and set **Base URL** to **LoadBalancerURL** value.
{{% /note %}}

## Testing scenarios

Using the Data Center App Performance Toolkit for [Performance and scale testing your Data Center app](/platform/marketplace/developing-apps-for-atlassian-data-center-products/) involves two test scenarios:

- [Performance regression](#testscenario1)
- [Scalability testing](#testscenario2)

Each scenario will involve multiple test runs. The following subsections explain both in greater detail.

### <a id="testscenario1"></a> Scenario 1: Performance regression

This scenario helps to identify basic performance issues without a need to spin up a multi-node Jira DC. Make sure the app does not have any performance impact when it is not exercised.

#### <a id="regressionrun1"></a> Run 1 (~50 min)

To receive performance baseline results without an app installed:

1. On the computer where you cloned the Data Center App Performance Toolkit, navigate to `dc-app-performance-toolkit/app folder`.
1. Open the `jira.yml` file and fill in the following variables:
    - `application_hostname`: your_dc_jira_instance_hostname without protocol
    - `application_protocol`: HTTP or HTTPS
    - `application_port`: for HTTP - 80, for HTTPS - 443, or your instance-specific port. The self-signed certificate is not supported.
    - `admin_login`: admin user username
    - `admin_password`: admin user password
    - `concurrency`: number of concurrent users for JMeter scenario - we recommend to use defaults for full-scale results generation.
    - `test_duration`: duration of the performance run - we recommend to use defaults for full-scale results generation.
    - `ramp-up`: amount of time it will take JMeter to add all test users to test execution - we recommend to use defaults for full-scale results generation.
1. Run bzt.

    ``` bash
    bzt jira.yml
    ```
1. View the following main results of the run in the `dc-app-performance-toolkit/app/results/jira/YY-MM-DD-hh-mm-ss` folder:
    - `results.csv`: aggregated .csv file with all actions and timings
    - `bzt.log`: logs of the Taurus tool execution
    - `jmeter.*`: logs of the JMeter tool execution
    - `pytest.*`: logs of Pytest-Selenium execution

{{% note %}}
When the execution is successfully completed, the `INFO: Artifacts dir:` line with the full path to results directory will be displayed in console output. Save this full path to the run results folder. Later you will have to insert it under `runName: "without app"` for report generation.
{{% /note %}}

#### <a id="regressionrun2"></a> Run 2 (~50 min + Lucene Index timing test)

{{% note %}}
**Lucene index test for JIRA**

If you are submitting a Jira app, you are required to conduct a Lucene Index timing test. This involves conducting a foreground re-index on a single-node Data Center deployment (without and with your app installed) and a dataset that has 1M issues.

Steps:

1. Go to **![cog icon](/platform/marketplace/images/cog.png) &gt; System &gt; Indexing**.
1. Select the **Lock one Jira node and rebuild index** option.
1. Click **Re-Index** and wait until re-indexing is completed.
1. **Take a screenshot of the acknowledgment screen** displaying the re-index time and attach it to your DC HELP ticket.

{{% /note %}}

{{% note %}}
Jira 7 index time for 1M issues on a User Guide recommended configuration is about ~100 min, Jira 8 index time is about ~40 min.
{{% /note %}}

To receive performance results with an app installed and Lucene index timing screenshots:

1. Follow the steps described in Note section to get a Lucene index timing screenshot without an app installed.
1. Install the app you want to test.
1. Follow the steps described in Note section to get a Lucene index timing screenshot with an app installed.
1. Run bzt.

    ``` bash
    bzt jira.yml
    ```

{{% note %}}
When the execution is successfully completed, the `INFO: Artifacts dir:` line with the full path to results directory will be displayed in console output. Save this full path to the run results folder. Later you will have to insert it under `runName: "with app"` for report generation.
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
1. In the `dc-app-performance-toolkit/app/results/reports/YY-MM-DD-hh-mm-ss` folder, view the `.csv` file (with consolidated scenario results) and the `.png` file.

#### Analyzing report

Once completed, you will be able to review the action timings with and without your app to see its impact on the performance of the instance. If you see a significant impact (>10%) on any action timing, we recommend taking a look into the app implementation to understand the root cause of this delta.


### <a id="testscenario2"></a> Scenario 2: Scalability testing

The purpose of scalability testing is to reflect the impact on the customer experience when operating across multiple nodes. For this, you have to run scale testing on your app.

For many apps and extensions to Atlassian products, there should not be a significant performance difference between operating on a single node or across many nodes in Jira DC deployment. To demonstrate performance impacts of operating your app at scale, we recommend testing your Jira DC app in a cluster.

#### Extending the base action

Extension scripts, which extend the base JMeter (`jira.jmx`) and Selenium (`jira-ui.py`) scripts, are located in a separate folder (`dc-app-performance-toolkit/extension/jira`). You can modify these scripts to include their app-specific actions.

##### Modifying JMeter

JMeter is written in XML and requires JMeter GUI to view and make changes. You can launch JMeter GUI by running the `~/.bzt/jmeter-taurus/<jmeter_version>/bin/jmeter` command.

Make sure you run this command inside the `dc-app-performance-toolkit/app directory`. The main `jmeter/jira.jmx` file contains relative paths to other scripts and will throw errors if run and loaded elsewhere.

Here's a snippet of the base JMeter script (`jira.jmx`):

![Base JMeter script](/platform/marketplace/images/jmeter-base.png)

For every base action, there is an extension script executed after the base script. In most cases, you should modify only the `extension.jmx` file. For example, if there are additional REST APIs introduced as part of viewing an issue, you can include these calls in the `extension.jmx` file under the view issue transaction.

Here's a snippet of the extension JMeter script (`extension.jmx`).

![Extended JMeter script](/platform/marketplace/images/jmeter-extended.png)

This ensures that these APIs are called as part of the view issue transaction with minimal intrusion (for example, no additional logins). For a fairer comparison, you have to keep the same number of base transactions before and after the plugin is installed.

{{% note %}}
The controllers in the extension script, which are executed along with the base action, are named after the corresponding base action (for example, `extend_search_jql`, `extend_view_issue`).
{{% /note %}}

When debugging, if you want to only test transactions in the `extend_view_issue` action, you can comment out other transactions in the `jira.yml` config file and set the percentage of the base execution to 100. Alternatively, you can change percentages of others to 0.

``` yml
#      perc_create_issue: 4
#      perc_search_jql: 16
      perc_view_issue: 100
#      perc_view_project_summary: 4
#      perc_view_dashboard: 8
```

{{% note %}}
If multiple actions are affected, add transactions to multiple extension controllers.
{{% /note %}}

##### Extending a stand-alone transaction

You can run your script independently of the base action under a specific workload if, for example, your plugin introduces a separate URL and has no correlation to the base transactions.

In such a case, you extend the `extend_standalone_extension` controller, which is also located in the `extension.jmx` file. With this option, you can define the execution percentage by the `perc_standalone_extension` parameter in the `jira.yml` config file.

The following configuration ensures that extend_standalone_extension controller is executed 10% of the total transactions.

``` yml
      perc_standalone_extension: 10
```

##### Using JMeter variables from the base script

Use or access the following variables of the extension script from the base script. They can also be inherited.

- `${issue_key}` - issue key being viewed or modified (e.g. ABC-123)
- `${issue_id}` - issue id being viewed or modified (e.g. 693484)
- `${project_key}` - project key being viewed or modified (e.g. ABC)
- `${project_id}` - project id being viewed or modified (e.g. 3423)
- `${scrum_board_id}` - scrum board id being viewed (e.g. 328)
- `${kanban_board_id}` - kanban board id being viewed (e.g. 100)
- `${jql}` - jql query being used (e.g. text ~ "qrk*" order by key)
- `${username}` - the logged in username (e.g. admin)

{{% note %}}
If there are some additional variables from the base script required by the extension script, you can add variables to the base script using extractors. For more information, go to [Regular expression extractors](http://jmeter.apache.org/usermanual/component_reference.html#Regular_Expression_Extractor).
{{% /note %}}

##### Modifying Selenium

In addition to JMeter, you can extend Selenium scripts to measure the end-to-end browser timings.

We use **Pytest** to drive Selenium tests. The `jira-ui.py` executor script is located in the `app/selenium_ui/` folder. This file contains all browser actions, defined by the `test_ functions`. These actions are executed one by one during the testing.

In the `jira-ui.py` script, view the following block of code:

``` python
# def test_1_selenium_custom_action(webdriver, datasets, screen_shots):
#     custom_action(webdriver, datasets)
```

This is a placeholder to add an extension action. The custom action can be moved to a different line, depending on the required workflow, as long as it is between the login (`test_0_selenium_a_login`) and logout (`test_2_selenium_z_log_out`) actions.

To implement the custom_action function, modify the `extension_ui.py` file in the `extension/jira/` directory. The following is an example of the `custom_action` function, where Selenium navigates to a URL, clicks on an element, and waits until an element is visible:

``` python
def custom_action(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        @print_timing
        def measure(webdriver, interaction):
            webdriver.get(f'{APPLICATION_URL}/plugins/servlet/some-app/reporter')
            WebDriverWait(webdriver, timeout).until(EC.visibility_of_element_located((By.ID, 'plugin-element')))
        measure(webdriver, 'selenium_app_custom_action:view_report')
```

To view more examples, see the `modules.py` file in the `selenium_ui/jira` directory.

#### Running tests with your modification

To ensure that the test runs without errors in parallel, run your extension scripts with the base scripts as a sanity check.

##### <a id="run3"></a> Run 3 (~50 min)
To receive scalability benchmark results for one-node Jira DC with app-specific actions, run `bzt`:

``` bash
bzt jira.yml
```

{{% note %}}
When the execution is successfully completed, the `INFO: Artifacts dir:` line with the full path to results directory will be displayed.
Save this full path to the run results folder. Later you will have to insert it under `runName: "Node 1"` for report generation.
{{% /note %}}

##### <a id="run4"></a> Run 4 (~50 min)

To receive scalability benchmark results for two-node Jira DC with app-specific actions:

1. In the AWS console, go to **CloudFormation > Stack details > Select your stack**.
1. On the **Update** tab, select **Use current template**, and then click **Next**.
1. Enter `2` in the **Maximum number of cluster nodes** and the **Minimum number of cluster nodes** fields.
1. Click **Next > Next > Update stack** and wait until stack is updated.
1. Make sure that Jira index successfully synchronized to the second node. To do that, use SSH to connect to the second node via Bastion (where `NODE_IP` is the IP of the second node):

    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NODE_IP=node_private_ip
    export SSH_OPTS='-o ServerAliveInterval=60 -o ServerAliveCountMax=30'
    ssh ${SSH_OPTS} -o "proxycommand ssh -W %h:%p ${SSH_OPTS} ec2-user@$BASTION_IP" ec2-user@${NODE_IP}
    ```
1. Once you're in the second node, download the [index-sync.sh](https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/jira/index-sync.sh) file. Then, make it executable and run it:

    ```bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/jira/index-sync.sh && chmod +x index-sync.sh
    ./index-sync.sh | tee -a index-sync.log
    ```
    Index synchronizing time is about 5-10 minutes. When index synchronizing is successfully completed, the following lines will be displayed in console output:
    ```bash
    IndexCopyService] Index restore started. Total 0 issues on instance before loading Snapshot file: IndexSnapshot_10203.tar.sz
    Recovering search indexes - 60% complete... Recovered added and updated issues
    Recovering search indexes - 80% complete... Cleaned removed issues
    Recovering search indexes - 100% complete... Recovered all indexes
    IndexCopyService] Index restore complete. Total N issues on instance
    ```
1. Run bzt.

    ``` bash
    bzt jira.yml
    ```    

{{% note %}}
When the execution is successfully completed, the `INFO: Artifacts dir:` line with the full path to results directory will be displayed in console output. Save this full path to the run results folder. Later you will have to insert it under `runName: "Node 2"` for report generation.
{{% /note %}}

##### <a id="run5"></a> Run 5 (~50 min)

To receive scalability benchmark results for four-node Jira DC with app-specific actions:

1. Scale your Jira Data Center deployment to 4 nodes the same way as in [Run 4](#run4).
1. Check Index is synchronized to new nodes the same way as in [Run 4](#run4).
1. Run bzt.

    ``` bash
    bzt jira.yml
    ```    

{{% note %}}
When the execution is successfully completed, the `INFO: Artifacts dir:` line with the full path to results directory will be displayed in console output.
Save this full path to the run results folder. Later you will have to insert it under `runName: "Node 4"` for report generation.
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
1. In the `dc-app-performance-toolkit/app/results/reports/YY-MM-DD-hh-mm-ss` folder, view the `.csv` file (with consolidated scenario results) and the `.png` file.

#### Analyzing report

Once completed, you will be able to review action timings on Jira Data Center with different numbers of nodes. If you see a significant variation in any action timings between configurations, we recommend taking a look into the app implementation to understand the root cause of this delta.

After completing all your tests, delete your Jira Data Center stacks.
