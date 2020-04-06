---
title: "Data Center App Performance Toolkit User Guide For Confluence"
platform: platform
product: marketplace
category: devguide
subcategory: build
date: "2018-07-19"
---
# Data Center App Performance Toolkit User Guide For Confluence

To use the Data Center App Performance Toolkit, you'll need to first clone its repo.

``` bash
git clone git@github.com:atlassian/dc-app-performance-toolkit.git
```

Follow installation instructions described in the `dc-app-performance-toolkit/README.md` file.

If you need performance testing results at a production level, follow instructions in this chapter to set up Confluence Data Center with the corresponding dataset.

For spiking, testing, or developing, your local Confluence instance would work well. Thus, you can skip this chapter and proceed with [Testing scenarios](/platform/marketplace/dc-apps-performance-toolkit-user-guide-confluence/#testing-scenarios). Still, script adjustments for your local dataset may be required.

## Setting up Confluence Data Center

We recommend that you use the [AWS Quick Start for Confluence Data Center](https://aws.amazon.com/quickstart/architecture/confluence/) to deploy a Confluence Data Center testing environment. This Quick Start will allow you to deploy Confluence Data Center with a new [Atlassian Standard Infrastructure](https://aws.amazon.com/quickstart/architecture/atlassian-standard-infrastructure/) (ASI) or into an existing one.

The ASI is a Virtual Private Cloud (VPC) consisting of subnets, NAT gateways, security groups, bastion hosts, and other infrastructure components required by all Atlassian applications, and then deploys Confluence into this new VPC. Deploying Confluence with a new ASI takes around 50 minutes. With an existing one, it'll take around 30 minutes.

### Using the AWS Quick Start for Confluence

If you are a new user, perform an end-to-end deployment. This involves deploying Confluence into a _new_ ASI.

If you have already deployed the ASI separately by using the [ASI Quick Start](https://aws.amazon.com/quickstart/architecture/atlassian-standard-infrastructure/)ASI Quick Start or by deploying another Atlassian product (Jira, Bitbucket, or Confluence Data Center), deploy Confluence into your existing ASI.

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
| One Node Confluence DC | 1.5 - 1.6 |
| Two Nodes Confluence DC | 1.7 - 2.5 |
| Four Nodes Confluence DC | 3.5 - 4.2 |

#### Quick Start parameters

All important parameters are listed and described in this section. For all other remaining parameters, we recommend using the Quick Start defaults.

**Confluence setup**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Collaborative editing mode | synchrony-local |
| Confluence Version | 6.13.8 or 7.0.4 |

The Data Center App Performance Toolkit officially supports:

- The latest Confluence Platform Release version: 7.0.4 
- The latest Confluence [Enterprise Release](https://confluence.atlassian.com/enterprise/atlassian-enterprise-releases-948227420.html): 6.13.8

**Cluster nodes**

| Parameter | Recommended Value |
| ----------| ----------------- |
| Cluster node instance type | [c5.4xlarge](https://aws.amazon.com/ec2/instance-types/c5/) |
| Maximum number of cluster nodes | 1 |
| Minimum number of cluster nodes | 1 |
| Cluster node instance volume size | 200 |

We recommend [c5.4xlarge](https://aws.amazon.com/ec2/instance-types/c5/) to strike the balance between cost and hardware we see in the field for our enterprise customers. More info could be found in public [recommendations](https://confluence.atlassian.com/enterprise/infrastructure-recommendations-for-enterprise-confluence-instances-on-aws-965544795.html).

The Data Center App Performance Toolkit framework is also set up for concurrency we expect on this instance size. As such, underprovisioning will likely show a larger performance impact than expected.

**Database**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Database instance class | [db.m4.xlarge](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html#Concepts.DBInstanceClass.Summary) |
| RDS Provisioned IOPS | 1000 |
| Master (admin) password | Password1! |
| Enable RDS Multi-AZ deployment | true |
| Application user database password | Password1! |
| Database storage | 200 |

{{% note %}}
The **Master (admin) password** will be used later when restoring the SQL database dataset. If password value is not set to default, you'll need to change `DB_PASS` value manually in the restore database dump script (later in [Preloading your Confluence deployment with an enterprise-scale dataset](#preloading)).
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

After successfully deploying Confluence Data Center in AWS, you'll need to configure it:

1. In the AWS console, go to **Services > CloudFormation > Stack > Stack details > Select your stack**.
1. On the **Outputs** tab, copy the value of the **LoadBalancerURL** key.
1. Open **LoadBalancerURL** in your browser. This will take you to the Confluence setup wizard.
1. On the **Get apps** page, do not select addition apps, just click **Next**.
1. On the next page, populate the **Your License Key** field by either:
    - Using your existing license, or
    - Generating an evaluation license, or
    - Contacting Atlassian to be provided two time-bomb licenses for testing. Ask for it in your DCHELP ticket.
    Click **Next**.
1. On the **Load Content** page, click on the **Empty Site**.
1. On the **Configure User Management** page, click on the **Mane users and groups within Confluence**.
1. On the **Configure System Administrator Account** page, populate the following fields:
    - **Username**: admin _(recommended)_
    - **Name**: admin _(recommended)_
    - **Email Address**: email address of the admin user
    - **Password**: admin _(recommended)_
    - **Confirm Password**: admin _(recommended)_
    Click **Next**.
1. On the **Setup Successful** page, click on the **Start**.
1. After going through the welcome setup, enter any **Space name** to create an initial space and click **Continue**.
1. Enter the first page title and click **Publish**.

{{% note %}}
After [Preloading your Confluence deployment with an enterprise-scale dataset](#preloading), the admin user will have `admin`/`admin` credentials.
{{% /note %}}

## <a id="preloading"></a> Preloading your Confluence deployment with an enterprise-scale dataset

Data dimensions and values for an enterprise-scale dataset are listed and described in the following table.

| Data dimensions | Value for an enterprise-scale dataset |
| --------------- | ------------------------------------- |
| Pages | ~900 000 |
| Blogposts | ~100 000 |
| Attachments | ~2 300 000 |
| Comments | ~6 000 000 |
| Spaces  | ~5 000 |
| Users | ~5 000 |

{{% note %}}
All the datasets use the standard `admin`/`admin` credentials.
{{% /note %}}

Pre-loading the dataset is a three-step process:

1. [Importing the main dataset](#importingdataset). To help you out, we provide an enterprise-scale dataset you can import either via the [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/confluence/populate_db.sh) script.
1. [Restoring attachments](#copyingattachments). We also provide attachments, which you can pre-load via an [upload_attachments.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/confluence/upload_attachments.sh) script.
1. [Re-indexing Confluence Data Center](#reindexing). For more information, go to [Re-indexing Confluence](https://confluence.atlassian.com/doc/content-index-administration-148844.html).

The following subsections explain each step in greater detail.

### <a id="importingdataset"></a> Importing the main dataset

You can load this dataset directly into the database (via a [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/confluence/populate_db.sh) script).  

#### Loading the dataset via populate_db.sh script (~90 min)

{{% note %}}
We recommend doing this via the CLI.
{{% /note %}}

To populate the database with SQL:

1. In the AWS console, go to **Services > EC2 > Instances**.
1. On the **Description** tab, do the following:
    - Copy the _Public IP_ of the Bastion instance.
    - Copy the _Private IP_ of the Confluence node instance.
1. Using SSH, connect to the Confluence node via the Bastion instance:

    For Windows, use Putty to connect to the Confluence node over SSH.
    For Linux or MacOS:
    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NODE_IP=node_private_ip
    export SSH_OPTS='-o ServerAliveInterval=60 -o ServerAliveCountMax=30'
    ssh ${SSH_OPTS} -o "proxycommand ssh -W %h:%p ${SSH_OPTS} ec2-user@${BASTION_IP}" ec2-user@${NODE_IP}
    ```
    For more information, go to [Connecting your nodes over SSH](https://confluence.atlassian.com/adminjiraserver/administering-jira-data-center-on-aws-938846969.html#AdministeringJiraDataCenteronAWS-ConnectingtoyournodesoverSSH).
1. Download the [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/confluence/populate_db.sh) script and make it executable:

    ``` bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/confluence/populate_db.sh && chmod +x populate_db.sh
    ```
1. Review the following `Variables section` of the script:

    ``` bash
    INSTALL_PSQL_CMD="amazon-linux-extras install -y postgresql10"
    DB_CONFIG="/var/atlassian/application-data/confluence/confluence.cfg.xml"
    CONFLUENCE_CURRENT_DIR="/opt/atlassian/confluence/current"
    CONFLUENCE_DB_NAME="confluence"
    CONFLUENCE_DB_USER="postgres"
    CONFLUENCE_DB_PASS="Password1!"
    CONFLUENCE_VERSION_FILE="/media/atl/confluence/shared-home/confluence.version"
    DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/confluence"
    ```
1. Run the script:

    ``` bash
    ./populate_db.sh | tee -a populate_db.log
    ```

{{% note %}}
Do not close or interrupt the session. It will take some time to restore SQL database. When SQL restoring is finished, an admin user will have `admin`/`admin` credentials.

In case of a failure, check the `Variables` section and run the script one more time.
{{% /note %}}

### <a id="copyingattachments"></a> Restoring attachments (~3 hours)

After [Importing the main dataset](#importingdataset), you'll now have to pre-load an enterprise-scale set of attachments.

1. Using SSH, connect to the Confluence node via the Bastion instance:

    For Windows, use Putty to connect to the Confluence node over SSH.
    For Linux or MacOS:
    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NODE_IP=node_private_ip
    export SSH_OPTS='-o ServerAliveInterval=60 -o ServerAliveCountMax=30'
    ssh ${SSH_OPTS} -o "proxycommand ssh -W %h:%p ${SSH_OPTS} ec2-user@${BASTION_IP}" ec2-user@${NODE_IP}
    ```
    For more information, go to [Connecting your nodes over SSH](https://confluence.atlassian.com/adminjiraserver/administering-jira-data-center-on-aws-938846969.html#AdministeringJiraDataCenteronAWS-ConnectingtoyournodesoverSSH).
1. Download the [upload_attachments.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/confluence/upload_attachments.sh) script and make it executable:

    ``` bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/confluence/upload_attachments.sh && chmod +x upload_attachments.sh
    ```    
1. Review the following `Variables section` of the script:

    ``` bash
    DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/confluence"
    ATTACHMENTS_TAR="attachments.tar.gz"
    ATTACHMENTS_DIR="attachments"
    TMP_DIR="/tmp"
    EFS_DIR="/media/atl/confluence/shared-home"
    ```
1. Run the script:

    ``` bash
    ./upload_attachments.sh | tee -a upload_attachments.log
    ```

{{% note %}}
Do not close or interrupt the session. It will take some time to upload attachments to Elastic File Storage (EFS).
{{% /note %}}

### <a id="reindexing"></a> Re-indexing Confluence Data Center (~2-4 hours)

{{% note %}}
Before re-index, go to **![cog icon](/platform/marketplace/images/cog.png) &gt; General configuration &gt; General configuration**, click **Edit** for **Site Configuration** and set **Base URL** to **LoadBalancerURL** value.
{{% /note %}}

For more information, go to [Re-indexing Confluence](https://confluence.atlassian.com/doc/content-index-administration-148844.html).

1. Log in as a user with the **Confluence System Administrators** [global permission](https://confluence.atlassian.com/doc/global-permissions-overview-138709.html).
1. Go to **![cog icon](/platform/marketplace/images/cog.png) &gt; General Configuration &gt; Content Indexing**.
1. Click **Rebuild** and wait until re-indexing is completed.

Confluence will be unavailable for some time during the re-indexing process.

### <a id="index-snapshot"></a> Create Index Snapshot (~30 min)

For more information, go to [Administer your Data Center search index](https://confluence.atlassian.com/doc/administer-your-data-center-search-index-879956107.html).

1. Log in as a user with the **Confluence System Administrators** [global permission](https://confluence.atlassian.com/doc/global-permissions-overview-138709.html).
1. Create any new page with a random content (without a new page index snapshot job will not be triggered).
1. Go to **![cog icon](/platform/marketplace/images/cog.png) &gt; General Configuration &gt; Scheduled Jobs**.
1. Find **Clean Journal Entries** job and click **Run**.
1. Make sure that Confluence index snapshot was created. To do that, use SSH to connect to the Confluence node via Bastion (where `NODE_IP` is the IP of the node):

    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NODE_IP=node_private_ip
    export SSH_OPTS='-o ServerAliveInterval=60 -o ServerAliveCountMax=30'
    ssh ${SSH_OPTS} -o "proxycommand ssh -W %h:%p ${SSH_OPTS} ec2-user@${BASTION_IP}" ec2-user@${NODE_IP}
    ```
1. Download the [index-snapshot.sh](https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/confluence/index-snapshot.sh) file. Then, make it executable and run it:

    ```bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/confluence/index-snapshot.sh && chmod +x index-snapshot.sh
    ./index-snapshot.sh | tee -a index-snapshot.log
    ```
    Index snapshot creation time is about 20-30 minutes. When index snapshot is successfully created, the following will be displayed in console output:
    ```bash
    Snapshot was created successfully.
    ```

## Testing scenarios

Using the Data Center App Performance Toolkit for [Performance and scale testing your Data Center app](/platform/marketplace/developing-apps-for-atlassian-data-center-products/) involves two test scenarios:

- [Performance regression](#testscenario1)
- [Scalability testing](#testscenario2)

Each scenario will involve multiple test runs. The following subsections explain both in greater detail.

### <a id="testscenario1"></a> Scenario 1: Performance regression

This scenario helps to identify basic performance issues without a need to spin up a multi-node Confluence DC. Make sure the app does not have any performance impact when it is not exercised.

#### <a id="regressionrun1"></a> Run 1 (~50 min)

To receive performance baseline results without an app installed:

1. On the computer where you cloned the Data Center App Performance Toolkit, navigate to `dc-app-performance-toolkit/app folder`.
1. Open the `confluence.yml` file and fill in the following variables:
    - `application_hostname`: your_dc_confluence_instance_hostname without protocol
    - `application_protocol`: HTTP or HTTPS
    - `application_port`: for HTTP - 80, for HTTPS - 443, or your instance-specific port. The self-signed certificate is not supported.
    - `admin_login`: admin user username
    - `admin_password`: admin user password
    - `concurrency`: number of concurrent users for JMeter scenario - we recommend you use the defaults to generate full-scale results.
    - `test_duration`: duration of the performance run - we recommend you use the defaults to generate full-scale results.
    - `ramp-up`: amount of time it will take JMeter to add all test users to test execution - we recommend you use the defaults to generate full-scale results.
1. Run bzt.

    ``` bash
    bzt confluence.yml
    ```
1. View the following main results of the run in the `dc-app-performance-toolkit/app/results/confluence/YY-MM-DD-hh-mm-ss` folder:
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


#### <a id="regressionrun2"></a> Run 2 (~50 min)

To receive performance results with an app installed:

1. Install the app you want to test.
1. Run bzt.

    ``` bash
    bzt confluence.yml
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

For many apps and extensions to Atlassian products, there should not be a significant performance difference between operating on a single node or across many nodes in Confluence DC deployment. To demonstrate performance impacts of operating your app at scale, we recommend testing your Confluence DC app in a cluster.

#### Extending the base action

Extension scripts, which extend the base JMeter (`confluence.jmx`) and Selenium (`confluence-ui.py`) scripts, are located in a separate folder (`dc-app-performance-toolkit/app/extension/confluence`). You can modify these scripts to include their app-specific actions.

##### Modifying JMeter

JMeter is written in XML and requires JMeter GUI to view and make changes. You can launch JMeter GUI by running the `~/.bzt/jmeter-taurus/<jmeter_version>/bin/jmeter` command.

Make sure you run this command inside the `dc-app-performance-toolkit/app directory`. The main `jmeter/confluence.jmx` file contains relative paths to other scripts and will throw errors if run and loaded elsewhere.

Here's a snippet of the base JMeter script (`confluence.jmx`):

![Base JMeter script](/platform/marketplace/images/jmeter-base.png)

For every base action, there is an extension script executed after the base script. In most cases, you should modify only the `extension.jmx` file. For example, if there are additional REST APIs introduced as part of viewing an issue, you can include these calls in the `extension.jmx` file under the view issue transaction.

Here's a snippet of the extension JMeter script (`extension.jmx`).

![Extended JMeter script](/platform/marketplace/images/jmeter-extended.png)

This ensures that these APIs are called as part of the view issue transaction with minimal intrusion (for example, no additional logins). For a fairer comparison, you have to keep the same number of base transactions before and after the plugin is installed.

{{% note %}}
The controllers in the extension script, which are executed along with the base action, are named after the corresponding base action (for example, `extend_search_jql`, `extend_view_issue`).
{{% /note %}}

When debugging, if you want to only test transactions in the `extend_view_issue` action, you can comment out other transactions in the `confluence.yml` config file and set the percentage of the base execution to 100. Alternatively, you can change percentages of others to 0.

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

In such a case, you extend the `extend_standalone_extension` controller, which is also located in the `extension.jmx` file. With this option, you can define the execution percentage by the `perc_standalone_extension` parameter in the `confluence.yml` config file.

The following configuration ensures that extend_standalone_extension controller is executed 10% of the total transactions.

``` yml
      perc_standalone_extension: 10
```

##### Using JMeter variables from the base script

Use or access the following variables of the extension script from the base script. They can also be inherited.

- `${blog_id}` - blog post id being viewed or modified (e.g. 23766699)
- `${blog_space_key}` - blog space key (e.g. PFSEK)
- `${page_id}` - page if being viewed or modified (e.g. 360451)
- `${space_key}` - page space key (e.g. TEST)
- `${file_path}` - path of file to upload (e.g. datasets/confluence/static-content/upload/test5.jpg)
- `${file_type}` - type of the file (e.g. image/jpeg)
- `${file_name}` - name of the file (e.g. test5.jpg)
- `${username}` - the logged in username (e.g. admin)

{{% note %}}
If there are some additional variables from the base script required by the extension script, you can add variables to the base script using extractors. For more information, go to [Regular expression extractors](http://jmeter.apache.org/usermanual/component_reference.html#Regular_Expression_Extractor).
{{% /note %}}

##### Modifying Selenium

In addition to JMeter, you can extend Selenium scripts to measure the end-to-end browser timings.

We use **Pytest** to drive Selenium tests. The `confluence-ui.py` executor script is located in the `app/selenium_ui/` folder. This file contains all browser actions, defined by the `test_ functions`. These actions are executed one by one during the testing.

In the `confluence-ui.py` script, view the following block of code:

``` python
# def test_1_selenium_custom_action(webdriver, datasets, screen_shots):
#     custom_action(webdriver, datasets)
```

This is a placeholder to add an extension action. The custom action can be moved to a different line, depending on the required workflow, as long as it is between the login (`test_0_selenium_a_login`) and logout (`test_2_selenium_z_log_out`) actions.

To implement the custom_action function, modify the `extension_ui.py` file in the `extension/confluence/` directory. The following is an example of the `custom_action` function, where Selenium navigates to a URL, clicks on an element, and waits until an element is visible:

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

To view more examples, see the `modules.py` file in the `selenium_ui/confluence` directory.

#### Running tests with your modification

To ensure that the test runs without errors in parallel, run your extension scripts with the base scripts as a sanity check.

##### <a id="run3"></a> Run 3 (~50 min)
To receive scalability benchmark results for one-node Confluence DC with app-specific actions, run `bzt`:

``` bash
bzt confluence.yml
```

{{% note %}}
When the execution is successfully completed, the `INFO: Artifacts dir:` line with the full path to results directory will be displayed.
Save this full path to the run results folder. Later you will have to insert it under `runName: "Node 1"` for report generation.
{{% /note %}}

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps.
{{% /note %}}


##### <a id="run4"></a> Run 4 (~50 min)

To receive scalability benchmark results for two-node Confluence DC with app-specific actions:

1. In the AWS console, go to **CloudFormation > Stack details > Select your stack**.
1. On the **Update** tab, select **Use current template**, and then click **Next**.
1. Enter `2` in the **Maximum number of cluster nodes** and the **Minimum number of cluster nodes** fields.
1. Click **Next > Next > Update stack** and wait until stack is updated.
1. Make sure that Confluence index successfully synchronized to the second node. To do that, use SSH to connect to the second node via Bastion (where `NODE_IP` is the IP of the second node):

    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NODE_IP=node_private_ip
    export SSH_OPTS='-o ServerAliveInterval=60 -o ServerAliveCountMax=30'
    ssh ${SSH_OPTS} -o "proxycommand ssh -W %h:%p ${SSH_OPTS} ec2-user@${BASTION_IP}" ec2-user@${NODE_IP}
    ```
1. Once you're in the second node, download the [index-sync.sh](https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/confluence/index-sync.sh) file. Then, make it executable and run it:

    ```bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/confluence/index-sync.sh && chmod +x index-sync.sh
    ./index-sync.sh | tee -a index-sync.log
    ```
    Index synchronizing time is about 10-30 minutes. When index synchronizing is successfully completed, the following lines will be displayed in console output:
    ```bash
    Log file: /var/atlassian/application-data/confluence/logs/atlassian-confluence.log
    Index recovery is required for main index, starting now
    main index recovered from shared home directory
    ```
    
1. Run bzt.

    ``` bash
    bzt confluence.yml
    ```    

{{% note %}}
When the execution is successfully completed, the `INFO: Artifacts dir:` line with the full path to results directory will be displayed in console output. Save this full path to the run results folder. Later you will have to insert it under `runName: "Node 2"` for report generation.
{{% /note %}}

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps.
{{% /note %}}


##### <a id="run5"></a> Run 5 (~50 min)

To receive scalability benchmark results for four-node Confluence DC with app-specific actions:

1. Scale your Confluence Data Center deployment to 4 nodes the same way as in [Run 4](#run4).
1. Check Index is synchronized to new nodes the same way as in [Run 4](#run4).
1. Run bzt.

    ``` bash
    bzt confluence.yml
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

Once completed, you will be able to review action timings on Confluence Data Center with different numbers of nodes. If you see a significant variation in any action timings between configurations, we recommend taking a look into the app implementation to understand the root cause of this delta.

After completing all your tests, delete your Confluence Data Center stacks.

## Support
In case of technical questions, issues or problems with DC Apps Performance Toolkit, contact us for support in the [community Slack](http://bit.ly/dcapt_slack) **#data-center-app-performance-toolkit** channel.