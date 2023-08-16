---
title: "Data Center App Performance Toolkit User Guide For Jira Service Management (CloudFormation deployment)"
platform: platform
product: marketplace
category: devguide
subcategory: build
date: "2023-08-15"
---
# Data Center App Performance Toolkit User Guide For Jira Service Management (CloudFormation deployment)

This document walks you through the process of testing your app on Jira Service Management using the Data Center App Performance Toolkit. These instructions focus on producing the required [performance and scale benchmarks for your Data Center app](/platform/marketplace/dc-apps-performance-and-scale-testing/):

If your application relays or extends the functionality of **Insight** ([What is Insight?](https://confluence.atlassian.com/servicemanagementserver/what-is-insight-1044784313.html)):

Please, make sure you have enabled Insight-specific tests in the `jsm.yml` file, by setting `True` value next to the `insight` variable.


In this document, we cover the use of the Data Center App Performance Toolkit on two types of environments:

**[Development environment](#mainenvironmentdev)**: Jira Service Management Data Center environment for a test run of Data Center App Performance Toolkit and development of [app-specific actions](#appspecificactions). We recommend you use the [AWS Quick Start for Jira Data Center](https://aws.amazon.com/quickstart/architecture/jira/) with the parameters prescribed here.

1. [Set up a development environment Jira Service Management Data Center on AWS](#devinstancesetup).
2. [Load a "small" dataset for the development environment](#devdataset).
3. [Run toolkit on the development environment locally](#devtestscenario).
4. [Develop and test app-specific actions locally](#devappaction).

**[Enterprise-scale environment](#mainenvironmententerprise)**: Jira Service Management Data Center environment used to generate Data Center App Performance Toolkit test results for the Marketplace approval process. Preferably, use the [AWS Quick Start for Jira Data Center](https://aws.amazon.com/quickstart/architecture/jira/) with the parameters prescribed below. These parameters provision larger, more powerful infrastructure for your Jira Service Management Data Center.

5. [Set up an enterprise-scale environment Jira Service Management Data Center on AWS](#instancesetup).
6. [Load an enterprise-scale dataset on your Jira Service Management Data Center deployment](#preloading).
7. [Set up an execution environment for the toolkit](#executionhost).
8. [Running the test scenarios from execution environment against enterprise-scale Jira Service Management Data Center](#testscenario).

---

## <a id="mainenvironmentdev"></a>Development environment

Running the tests in a development environment helps familiarize you with the toolkit. It'll also provide you with a lightweight and less expensive environment for developing. Once you're ready to generate test results for the Marketplace Data Center Apps Approval process, run the toolkit in an **enterprise-scale environment**.

### <a id="devinstancesetup"></a>1. Setting up Jira Service Management Data Center development environment

We recommend that you set up development environment using the [AWS Quick Start for Jira Data Center](https://aws.amazon.com/quickstart/architecture/jira/) (**How to deploy** tab). All the instructions on this page are optimized for AWS. 


#### Using the AWS Quick Start for Jira Service Management

If you are a new user, perform an end-to-end deployment. This involves deploying Jira Service Management into a _new_ ASI:

Navigate to **[AWS Quick Start for Jira Data Center](https://aws.amazon.com/quickstart/architecture/jira/) &gt; How to deploy** tab **&gt; Deploy into a new ASI** link.

If you have already deployed the ASI separately by using the [ASI Quick Start](https://aws.amazon.com/quickstart/architecture/atlassian-standard-infrastructure/)ASI Quick Start or by deploying another Atlassian product (Jira, Bitbucket, or Confluence Data Center development environment) with ASI, deploy Jira Service Management into your existing ASI:

Navigate to **[AWS Quick Start for Jira Data Center](https://aws.amazon.com/quickstart/architecture/jira/) &gt; How to deploy** tab **&gt; Deploy into your existing ASI** link.

{{% note %}}
You are responsible for the cost of AWS services used while running this Quick Start reference deployment. This Quick Start doesn't have any additional prices. See [Amazon EC2 pricing](https://aws.amazon.com/ec2/pricing/) for more detail.
{{% /note %}}

To reduce costs, we recommend you to keep your deployment up and running only during the performance runs.

#### AWS cost estimation for the development environment

AWS Jira Service Management Data Center development environment infrastructure costs about 25 - 50$ per working week depending on such factors like region, instance type, deployment type of DB, and other.  

#### <a id="quick-start-parameters"></a> Quick Start parameters for development environment

All important parameters are listed and described in this section. For all other remaining parameters, we recommend using the Quick Start defaults.

**Jira setup**

| Parameter | Recommended value                                                                                                                                                                                      |
| --------- |--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Jira Product | ServiceManagement                                                                                                                                                                                      |
| Version | The Data Center App Performance Toolkit officially supports `4.20.24`, `5.4.8` ([Long Term Support release](https://confluence.atlassian.com/enterprise/atlassian-enterprise-releases-948227420.html)) |

**Cluster nodes**

| Parameter | Recommended value |
| --------- | ----------------- |
| Cluster node instance type | [t3.large](https://aws.amazon.com/ec2/instance-types/t3/) (we recommend this instance type for its good balance between price and performance in testing environments) |
| Maximum number of cluster nodes | 1 |
| Minimum number of cluster nodes | 1 |
| Cluster node instance volume size | 50 |


**Database**

| Parameter | Recommended value |
| --------- | ----------------- |
| The database engine to deploy with | PostgresSQL |
| The database engine version to use | 11 |
| Database instance class | [db.t3.medium](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html#Concepts.DBInstanceClass.Summary) |
| RDS Provisioned IOPS | 1000 |
| Master (admin) password | Password1! |
| Enable RDS Multi-AZ deployment | false |
| Application user database password | Password1! |
| Database storage | 200 |


**Networking (for new ASI)**

| Parameter | Recommended value |
| --------- | ----------------- |
| Trusted IP range | 0.0.0.0/0 _(for public access) or your own trusted IP range_ |
| Availability Zones | _Select two availability zones in your region_ |
| Permitted IP range | 0.0.0.0/0 _(for public access) or your own trusted IP range_ |
| Make instance internet facing | True |
| Key Name | _The EC2 Key Pair to allow SSH access. See [Amazon EC2 Key Pairs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html) for more info._ |

**Networking (for existing ASI)**

| Parameter | Recommended value |
| --------- | ----------------- |
| Make instance internet facing | True |
| Permitted IP range | 0.0.0.0/0 _(for public access) or your own trusted IP range_ |
| Key Name | _The EC2 Key Pair to allow SSH access. See [Amazon EC2 Key Pairs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html) for more info._ |

#### Running the setup wizard

After successfully deploying the Jira Service Management Data Center on AWS, configure it as follows:

1. In the AWS console, go to **Services** > **CloudFormation** > **Stack** > **Stack details** > **Select your stack**.
1. On the **Outputs** tab, copy the value of the **LoadBalancerURL** key.
1. Open **LoadBalancerURL** in your browser. This will take you to the Jira Service Management setup wizard.
1. On the **Set up application properties** page, fill in the following fields:
    - **Application Title**: any name for your Jira Service Management Data Center deployment
    - **Mode**: private
    - **Base URL**: your stack's Elastic LoadBalancer URL

    Then select **Next**.
1. On the next page, fill in the **Your License Key** field in one of the following ways:
    - Using your existing license
    - Generating a Jira Service Management trial license
    - Contacting Atlassian to be provided two time-bomb licenses for testing. Ask for the licenses in your ECOHELP ticket.

    Then select **Next**.
1. On the **Set up administrator account** page, fill in the following fields:
    - **Full name**: a full name of the admin user
    - **Email Address**: email address of the admin user
    - **Username**: admin _(recommended)_
    - **Password**: admin _(recommended)_
    - **Confirm Password**: admin _(recommended)_

    Then select **Next**.

1. On the **Set up email notifications** page, configure your email notifications, and then select **Finish**.
1. On the first page of the welcome setup select **English (United States)** language. Other languages are not supported by the toolkit.
1. After going through the welcome setup, select **Create new project** to create a new project.

---

### <a id="devdataset"></a>2. Upload "small" dataset for development environment  

You can load this dataset directly into the database (via a [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/populate_db.sh) script), or import it via XML.  

##### Option 1 (recommended): Loading the "small" dataset via populate_db.sh script

To populate the database with SQL:

1. In the AWS console, go to **Services** > **EC2** > **Instances**.
1. On the **Description** tab, do the following:
    - Copy the _Public IP_ of the Bastion instance.
    - Copy the _Private IP_ of the Jira Service Management node instance.
1. Using SSH, connect to the Jira Service Management node via the Bastion instance:
  
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
1. Download the [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/populate_db.sh) script and make it executable:

    ``` bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/jira/populate_db.sh && chmod +x populate_db.sh
    ```
1. Review the following `Variables section` of the script:

    ``` bash
    DB_CONFIG="/var/atlassian/application-data/jira/dbconfig.xml"
    JIRA_DB_NAME="jira"
    JIRA_DB_USER="postgres"
    JIRA_DB_PASS="Password1!"
    # JSM section
    JIRA_CURRENT_DIR="/opt/atlassian/jira-servicedesk/current"
    JIRA_SETENV_FILE="${JIRA_CURRENT_DIR}/bin/setenv.sh"
    JIRA_VERSION_FILE="/media/atl/jira/shared/jira-servicedesk.version"
    ```
1. Run the script:

    ``` bash
    ./populate_db.sh --jsm --small 2>&1 | tee -a populate_db.log
    ```

{{% note %}}
In case of a failure, check the `Variables` section and run the script one more time.
{{% /note %}}

##### Option 2: Loading the "small" dataset through XML import

We recommend that you only use this method if you are having problems with the [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/populate_db.sh) script.

1. In the AWS console, go to **Services** > **EC2** > **Instances**.
1. On the **Description** tab, do the following:
    - Copy the _Public IP_ of the Bastion instance.
    - Copy the _Private IP_ of the Jira Service Management node instance.
1. Using SSH, connect to the Jira Service Management node via the Bastion instance:

    For Linux or MacOS run following commands in terminal (for Windows use [Git Bash](https://git-scm.com/downloads) terminal):
    
    ``` bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NODE_IP=node_private_ip
    export SSH_OPTS1='-o ServerAliveInterval=60'
    export SSH_OPTS2='-o ServerAliveCountMax=30'
    ssh ${SSH_OPTS1} ${SSH_OPTS2} -o "proxycommand ssh -W %h:%p ${SSH_OPTS1} ${SSH_OPTS2} ec2-user@${BASTION_IP}" ec2-user@${NODE_IP}
    ```
    For more information, go to [Connecting your nodes over SSH](https://confluence.atlassian.com/adminjiraserver/administering-jira-data-center-on-aws-938846969.html#AdministeringJiraDataCenteronAWS-ConnectingtoyournodesoverSSH).
1. Download the xml_backup.zip file corresponding to your Jira Service Management version.

    ``` bash
    JSM_VERSION=$(sudo su jira -c "cat /media/atl/jira/shared/jira-servicedesk.version")
    sudo su jira -c "wget https://centaurus-datasets.s3.amazonaws.com/jsm/${JSM_VERSION}/small/xml_backup.zip -O /media/atl/jira/shared/import/xml_backup.zip"
    ```
1. Log in as a user with the **Jira System Administrators** [global permission](https://confluence.atlassian.com/adminjiraserver/managing-global-permissions-938847142.html).
1. Go to **![cog icon](/platform/marketplace/images/cog.png) &gt; System &gt; Restore System.** from the menu.
1. Populate the **File name** field with `xml_backup.zip`.
1. Click **Restore** and wait until the import is completed.

#### Restoring "small" dataset attachments

1. Using SSH, connect to the Jira Service Management node via the Bastion instance:

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
1. Download the [upload_attachments.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/upload_attachments.sh) script and make it executable:

    ``` bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/jira/upload_attachments.sh && chmod +x upload_attachments.sh
    ```    
1. Review the following `Variables section` of the script:

    ``` bash
    # JSM version file location
    JIRA_VERSION_FILE="/media/atl/jira/shared/jira-servicedesk.version"
    ```
1. Run the script:

    ``` bash
    ./upload_attachments.sh --jsm --small 2>&1 | tee -a upload_attachments.log
    ```

#### Re-indexing development environment Jira Service Management Data Center

For more information, go to [Re-indexing Jira](https://confluence.atlassian.com/adminjiraserver/search-indexing-938847710.html).
{{% note %}}
The re-index time for JSM 4.20.x is about ~30-50 minutes, while for JSM 5.4.x it can take significantly longer at around 110-130 minutes. This increase in re-index time is due to a known issue which affects Jira 5.4.x, and you can find more information about it in this ticket: [Re-Index: JSM 5.4.x](https://jira.atlassian.com/browse/JRASERVER-74787).
{{% /note %}}
1. Log in as a user with the **Jira System Administrators** [global permission](https://confluence.atlassian.com/adminjiraserver/managing-global-permissions-938847142.html).
1. Go to **![cog icon](/platform/marketplace/images/cog.png) &gt; System &gt; Indexing**.
1. Select the **Full re-index** option.
1. Click **Re-Index** and wait until re-indexing is completed.

When finished, the **Acknowledge** button will be available on the re-indexing page.

---

### <a id="devtestscenario"></a>3. Run toolkit on the development environment locally

{{% warning %}}
Make sure **English (United States)** language is selected as a default language on the **![cog icon](/platform/marketplace/images/cog.png) &gt; System &gt; General configuration** page. Other languages are **not supported** by the toolkit.
{{% /warning %}}

1. Clone [Data Center App Performance Toolkit](https://github.com/atlassian/dc-app-performance-toolkit) locally.
2. Follow the [README.md](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/README.md) instructions to set up toolkit locally.
3. Navigate to `dc-app-performance-toolkit/app` folder.
4. Open the `jsm.yml` file and fill in the following variables:
    - `application_hostname`: your_dc_jsm_instance_hostname without protocol.
    - `application_protocol`: http or https.
    - `application_port`: for HTTP - 80, for HTTPS - 443, 8080, 2990 or your instance-specific port.
    - `secure`: True or False. Default value is True. Set False to allow insecure connections, e.g. when using self-signed SSL certificate.
    - `application_postfix`: set to empty for CloudFormation deployment; e.g., /jira for url like this http://localhost:2990/jira.
    - `admin_login`: admin user username.
    - `admin_password`: admin user password.
    - `load_executor`: executor for load tests. Valid options are [jmeter](https://jmeter.apache.org/) (default) or [locust](https://locust.io/).
    - `concurrency_agents`: `1` - number of concurrent JMeter/Locust agents.
    - `concurrency_customers`: `1` - number of concurrent JMeter/Locust customers.
    - `test_duration`: `5m` - duration of the performance run.
    - `ramp-up`: `3s` - amount of time it will take JMeter or Locust to add all test users to test execution.
    - `total_actions_per_hour_agents`: `500` - number of total JMeter/Locust actions per hour for agents scenario.
    - `total_actions_per_hour_customers`: `1500` - number of total JMeter/Locust actions per hour customers scenario.
    - `WEBDRIVER_VISIBLE`: visibility of Chrome browser during selenium execution (False is by default).
    - `insight`: True or False. Default value is False. Set True to enable Insight specific tests.
    

5. In case your application relays or extends the functionality of **Insight**. Make sure to set `True` value next to `insight` variable.

6. Run bzt.

    ``` bash
    bzt jsm.yml
    ```

7. Review the resulting table in the console log. All JMeter/Locust and Selenium actions should have 95+% success rate.  
In case some actions does not have 95+% success rate refer to the following logs in `dc-app-performance-toolkit/app/results/jsm/YY-MM-DD-hh-mm-ss` folder:

    - `results_summary.log`: detailed run summary
    - `results.csv`: aggregated .csv file with all actions and timings
    - `bzt.log`: logs of the Taurus tool execution
    - `jmeter.*`: logs of the JMeter tool execution
    - `locust.*`: logs of the Locust tool execution (in case you use Locust as load_executor in jsm.yml)
    - `pytest.*`: logs of Pytest-Selenium execution

{{% warning %}}
Do not proceed with the next step until you have all actions 95+% success rate. Ask [support](#support) if above logs analysis did not help.
{{% /warning %}}

---

### <a id="devappaction"></a>4. Develop and test app-specific action locally
Data Center App Performance Toolkit has its own set of default test actions for Jira Service Management Data Center: JMeter/Locust and Selenium for load and UI tests respectively.     

**App-specific action** - action (performance test) you have to develop to cover main use cases of your application. Performance test should focus on the common usage of your application and not to cover all possible functionality of your app. For example, application setup screen or other one-time use cases are out of scope of performance testing.

1. Define main use case of your app. Usually it is one or two main app use cases.
1. Your app adds new UI elements in Jira Service Management Data Center - Selenium app-specific action has to be developed.
1. Your app introduces new endpoint or extensively calls existing Jira Service Management Data Center API - JMeter/Locust app-specific actions has to be developed.  
JMeter and Locust actions are interchangeable, so you could select the tool you prefer:

- JMeter - UI-based [performance tool](https://jmeter.apache.org/).
- Locust - code-based (Python requests library) [performance tool](https://locust.io/).


{{% note %}}
We strongly recommend developing your app-specific actions on the development environment to reduce AWS infrastructure costs.
{{% /note %}}


#### Custom dataset
You can filter your own app-specific issues for your app-specific actions.

1. Create app-specific service desk requests that have specific anchor in summary, e.g. *AppRequest* anchor and issues summaries like *AppRequest1*, *AppRequest2*, *AppRequest3*.
1. Go to the search page of your Jira Service Management Data Center - `JSM_URL/issues/?jql=` and select `Advanced`.
1. Write [JQL](https://www.atlassian.com/blog/jira-software/jql-the-most-flexible-way-to-search-jira-14) that filter just your request from step 1, e.g. `summary ~ 'AppRequest*'`.
1. Edit JSM configuration file `dc-app-performance-toolkit/app/jsm.yml`:  
    - `custom_dataset_query:` JQL from step 3.

Next time when you run toolkit, custom dataset issues will be stored to the `dc-app-performance-toolkit/app/datasets/jsm/custom-requests.csv` with columns: `request_id`, `request_key`, `service_desk_id`, `project_id`, `project_key`.

#### Example of app-specific Selenium action development with custom dataset  
You develop an app that adds some additional fields to specific types of Jira Service Management requests. In this case, you should develop Selenium app-specific action:
1. Create app-specific service desk requests with *AppRequest* anchor in summary: *AppRequest1*, *AppRequest2*, etc.
1. Go to the search page of your Jira Service Management Data Center - `JSM_URL/issues/?jql=` and check if JQL is correct: `summary  ~ 'AppRequest*'`.
1. Edit `dc-app-performance-toolkit/app/jsm.yml` configuration file and set `custom_dataset_query: summary  ~ 'AppRequest*'`.
1. Extend example of app-specific action for agent in `dc-app-performance-toolkit/app/extension/jsm/extension_ui_agents.py`.  
[Code example.](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/extension/jsm/extension_ui_agents.py)
So, our test has to open app-specific requests in agent view and measure time to load of this app-specific request.
1. Extend example of app-specific action for customer in `dc-app-performance-toolkit/app/extension/jsm/extension_ui_customers.py`.  
[Code example.](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/extension/jsm/extension_ui_customers.py)
So, our test has to open app-specific requests in portal view and measure time to load of this app-specific request.
1. If you need to run `app_specific_action` as specific user uncomment `app_specific_user_login` function in [code example](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/extension/jsm/extension_ui_agents.py). Note, that in this case `test_1_selenium_custom_action` should follow just before `test_2_selenium_agent_z_logout` or `test_2_selenium_customer_z_log_out` action.
1. In `dc-app-performance-toolkit/app/selenium_ui/jsm_ui_agents.py`, review and uncomment the following block of code to make newly created app-specific actions executed:
``` python
# def test_1_selenium_agent_custom_action(jsm_webdriver, jsm_datasets, jsm_screen_shots):
#     extension_ui_agents.app_specific_action(jsm_webdriver, jsm_datasets)
```

1. In `dc-app-performance-toolkit/app/selenium_ui/jsm_ui_customers.py`, review and uncomment the following block of code to make newly created app-specific actions executed:
``` python
# def test_1_selenium_customer_custom_action(jsm_webdriver, jsm_datasets, jsm_screen_shots):
#     extension_ui_customers.app_specific_action(jsm_webdriver, jsm_datasets)
```

1. Run toolkit with `bzt jsm.yml` command to ensure that all Selenium actions including `app_specific_action` are successful.

#### Example of app-specific Locust/JMeter action development

You develop an app that introduces new GET and POST endpoints in Jira Service Management Data Center. In this case, you should develop Locust or JMeter app-specific action.

**Locust app-specific action development example**

1. Extend example of app-specific action for agent in `dc-app-performance-toolkit/app/extension/jsm/extension_locust_agents.py`, so that test will call the endpoint with GET request, parse response use these data to call another endpoint with POST request and measure response time.  
[Code example.](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/extension/jsm/extension_locust_agents.py)
1. Extend example of app-specific action for customers in `dc-app-performance-toolkit/app/extension/jsm/extension_locust_customers.py`, so that test will call the endpoint with GET request, parse response use these data to call another endpoint with POST request and measure response time.  
[Code example.](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/extension/jsm/extension_locust_customers.py)
1. In `dc-app-performance-toolkit/app/jsm.yml` set `load_executor: locust` to make `locust` as load executor.
1. Set desired execution percentage for `agent_standalone_extension`/`customer_standalone_extension`. Default value is `0`, which means that `agent_standalone_extension`/`customer_standalone_extension` action will not be executed. Locust uses actions percentage as relative [weights](https://docs.locust.io/en/stable/writing-a-locustfile.html#weight-attribute), so if `some_action: 10` and `standalone_extension: 20` that means that `standalone_extension` will be called twice more.  
Set `agent_standalone_extension`/`customer_standalone_extension` weight in accordance with the expected frequency of your app use case compared with other base actions.
1. App-specific tests could be run (if needed) as a specific user. Use `@run_as_specific_user(username='specific_user_username', password='specific_user_password')` decorator for that.
1. Run toolkit with `bzt jsm.yml` command to ensure that all Locust actions including `app_specific_action` are successful.

**JMeter app-specific action development example**

1. Check that `jsm.yml` file has correct settings of `application_hostname`, `application_protocol`, `application_port`, `application_postfix`, etc.
1. Set desired execution percentage for `agent_standalone_extension` and/or `customer_standalone_extension`. Default values are `0`, which means that `agent_standalone_extension` and `customer_standalone_extension` actions will not be executed. 
For example, for app-specific action development you could set percentage of `agent_standalone_extension` and/or `customer_standalone_extension` to 100 and for all other actions to 0 - this way only `jmeter_agent_login_and_view_dashboard` and `agent_standalone_extension` or `jmeter_customer_login_and_view_dashboard` and `customer_standalone_extension` actions would be executed.
1. Navigate to `dc-app-performance-toolkit/app` folder and run from virtualenv(as described in `dc-app-performance-toolkit/README.md`):
    
    ``` bash
    python util/jmeter/start_jmeter_ui.py --app jsm --type agents
    # or
    python util/jmeter/start_jmeter_ui.py --app jsm --type customers  
    ```

1. Open `Agents`/`Customers` thread group > `actions per login` and navigate to `agent_standalone_extension`/`customer_standalone_extension`
![Jira Service Management JMeter standalone extension](/platform/marketplace/images/jsm-standalone-extension.png)
1. Add GET `HTTP Request`: right-click to `agent_standalone_extension`/`customer_standalone_extension`` > `Add` > `Sampler` `HTTP Request`, chose method GET and set endpoint in Path.
![Jira Service Management JMeter standalone GET](/platform/marketplace/images/jsm-standalone-get-request.png)
1. Add `Regular Expression Extractor`: right-click to to newly created `HTTP Request` > `Add` > `Post processor` > `Regular Expression Extractor`
![Jira Service Management JMeter standalone regexp](/platform/marketplace/images/jsm-standalone-regexp.png)
1. Add `Response Assertion`: right-click to newly created `HTTP Request` > `Add` > `Assertions` > `Response Assertion` and add assertion with `Contains`, `Matches`, `Equals`, etc types.
![Jira Service Management JMeter standalone assertions](/platform/marketplace/images/jsm-standalone-assertions.png)
1. Add POST `HTTP Request`: right-click to `agent_standalone_extension`/`customer_standalone_extension` > `Add` > `Sampler` `HTTP Request`, chose method POST, set endpoint in Path and add Parameters or Body Data if needed.
1. Right-click on `View Results Tree` and enable this controller.
1. Click **Start** button and make sure that `login_and_view_dashboard` and `agent_standalone_extension`/`customer_standalone_extension` are successful.
1. Right-click on `View Results Tree` and disable this controller. It is important to disable `View Results Tree` controller before full-scale results generation.
1. Click **Save** button.
1. To make `agent_standalone_extension`/`customer_standalone_extension` executable during toolkit run edit `dc-app-performance-toolkit/app/jsm.yml` and set execution percentage of `agent_standalone_extension`/`customer_standalone_extension` accordingly to your use case frequency.
1. App-specific tests could be run (if needed) as a specific user. In the `agent_standalone_extension`/`customer_standalone_extension` uncomment `login_as_specific_user` controller. Navigate to the `username:password` config element and update values for `app_specific_username` and `app_specific_password` names with your specific user credentials. Also make sure that you located your app-specific tests between `login_as_specific_user` and `login_as_default_user_if_specific_user_was_loggedin` controllers.
1. Run toolkit to ensure that all JMeter actions including `agent_standalone_extension` and/or `customer_standalone_extension` are successful.


##### Using JMeter variables from the base script

Use or access the following variables in your `agent_standalone_extension` action if needed:

- `${request_id}` - request id being viewed or modified (e.g. 693484)
- `${request_key}` - request key being viewed or modified (e.g. ABC-123)
- `${request_project_id}` - project id being viewed or modified (e.g. 3423)
- `${request_project_key}` - project key being viewed or modified (e.g. ABC)
- `${request_service_desk_id}` - service_desk_id being viewed or modified (e.g. 86)
- `${s_prj_key}` - "small" project (<10k requests per project) key being viewed or modified (e.g. ABC)
- `${s_prj_id}` - "small" project id being viewed or modified (e.g. 123)
- `${s_service_desk_id}` - "small" project service_desk_id being viewed or modified (e.g. 12)
- `${s_prj_total_req}` - "small" project total requests (e.g. 444)
- `${s_prj_all_open_queue_id}` - "small" project "all open" queue id (e.g. 44)
- `${s_created_vs_resolved_id}` - "small" project "created vs resolved" report id (e.g. 45)
- `${s_time_to_resolution_id}` - "small" project "time to resolution" report id (e.g. 46)
- `${m_prj_key}` - "medium" project (>10k and <100k requests per project) key being viewed or modified (e.g. ABC)
- `${m_prj_id}` - "medium" project id being viewed or modified (e.g. 123)
- `${m_service_desk_id}` - "medium" project service_desk_id being viewed or modified (e.g. 12)
- `${m_prj_total_req}` - "medium" project total requests (e.g. 444)
- `${m_prj_all_open_queue_id}` - "medium" project "all open" queue id (e.g. 44)
- `${m_created_vs_resolved_id}` - "medium" project "created vs resolved" report id (e.g. 45)
- `${m_time_to_resolution_id}` - "medium" project "time to resolution" report id (e.g. 46)
- `${username}` - the logged in username (e.g. admin)

Use or access the following variables in your `customer_standalone_extension` action if needed:
- `${s_service_desk_id}` - "small" project (<10k requests per project) service_desk_id being viewed or modified (e.g. 12)
- `${rt_project_id}` - project id (e.g. 12)
- `${rt_service_desk_id}` - service_desk_id (e.g. 12)
- `${rt_id}` - request type id for project with project id `${rt_project_id}` and service_desk_id `${rt_service_desk_id}` (e.g. 123)
- `${username}` - the logged in username (e.g. admin)

{{% warning %}}
App-specific actions are required. Do not proceed with the next step until you have completed app-specific actions development and got successful results from toolkit run.
{{% /warning %}}

---
## <a id="mainenvironmententerprise"></a> Enterprise-scale environment

After adding your custom app-specific actions, you should now be ready to run the required tests for the Marketplace Data Center Apps Approval process. To do this, you'll need an **enterprise-scale environment**.

### <a id="instancesetup"></a>5. Set up an enterprise-scale environment Jira Service Management Data Center on AWS

We recommend that you use the [AWS Quick Start for Jira Data Center](https://aws.amazon.com/quickstart/architecture/jira/) (**How to deploy** tab)  to deploy a Jira Service Management Data Center enterprise-scale environment. This Quick Start will allow you to deploy Jira Service Management Data Center with a new [Atlassian Standard Infrastructure](https://aws.amazon.com/quickstart/architecture/atlassian-standard-infrastructure/) (ASI) or into an existing one.

The ASI is a Virtual Private Cloud (VPC) consisting of subnets, NAT gateways, security groups, bastion hosts, and other infrastructure components required by all Atlassian applications, and then deploys Jira Service Management into this new VPC. Deploying Jira Service Management with a new ASI takes around 50 minutes. With an existing one, it'll take around 30 minutes.

#### Using the AWS Quick Start for Jira Service Management

If you are a new user, perform an end-to-end deployment. This involves deploying Jira Service Management into a _new_ ASI:

Navigate to **[AWS Quick Start for Jira Data Center](https://aws.amazon.com/quickstart/architecture/jira/) &gt; How to deploy** tab **&gt; Deploy into a new ASI** link.

If you have already deployed the ASI separately by using the [ASI Quick Start](https://aws.amazon.com/quickstart/architecture/atlassian-standard-infrastructure/)ASI Quick Start or by deploying another Atlassian product (Jira, Bitbucket, or Confluence Data Center development environment) with ASI, deploy Jira Service Management into your existing ASI:

Navigate to **[AWS Quick Start for Jira Data Center](https://aws.amazon.com/quickstart/architecture/jira/) &gt; How to deploy** tab **&gt; Deploy into your existing ASI** link.

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
| One Node Jira Service Management DC | 0.8 - 1.1
| Two Nodes Jira Service Management DC | 1.2 - 1.7
| Four Nodes Jira Service Management DC | 2.0 - 3.0

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

**Jira setup**

| Parameter | Recommended Value                                                                                                                                                                                      |
| --------- |--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Jira Product | ServiceManagement                                                                                                                                                                                      |
| Version | The Data Center App Performance Toolkit officially supports `4.20.24`, `5.4.8` ([Long Term Support release](https://confluence.atlassian.com/enterprise/atlassian-enterprise-releases-948227420.html)) |

**Cluster nodes**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Cluster node instance type | [m5.2xlarge](https://aws.amazon.com/ec2/instance-types/m5/) (This differs from our [public recommendation on c4.8xlarge](https://confluence.atlassian.com/enterprise/infrastructure-recommendations-for-enterprise-jira-instances-on-aws-969532459.html) for production instances but is representative for a lot of our Jira Service Management Data Center customers. The Data Center App Performance Toolkit framework is set up for concurrency we expect on this instance size. As such, underprovisioning will likely show a larger performance impact than expected.)|
| Maximum number of cluster nodes | 1 |
| Minimum number of cluster nodes | 1 |
| Cluster node instance volume size | 100 |

**Database**

| Parameter | Recommended Value |
| --------- | ----------------- |
| The database engine to deploy with | PostgresSQL |
| The database engine version to use | 11 |
| Database instance class | [db.m5.xlarge](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html#Concepts.DBInstanceClass.Summary) |
| RDS Provisioned IOPS | 1000 |
| Master (admin) password | Password1! |
| Enable RDS Multi-AZ deployment | false |
| Application user database password | Password1! |
| Database storage | 200 |

{{% note %}}
The **Master (admin) password** will be used later when restoring the SQL database dataset. If password value is not set to default, you'll need to change `DB_PASS` value manually in the restore database dump script (later in [Preloading your Jira Service Management deployment with an enterprise-scale dataset](#preloading)).
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

After successfully deploying Jira Service Management Data Center in AWS, you'll need to configure it:

1. In the AWS console, go to **Services** > **CloudFormation** > **Stack** > **Stack details** > **Select your stack**.
1. On the **Outputs** tab, copy the value of the **LoadBalancerURL** key.
1. Open **LoadBalancerURL** in your browser. This will take you to the Jira Service Management setup wizard.
1. On the **Set up application properties** page, populate the following fields:
    - **Application Title**: any name for your Jira Service Management Data Center deployment
    - **Mode**: Private
    - **Base URL**: your stack's Elastic LoadBalancer URL
    Click **Next**.
1. On the next page, populate the **Your License Key** field by either:
    - Using your existing license, or
    - Generating a Jira Service Management trial license, or
    - Contacting Atlassian to be provided two time-bomb licenses for testing. Ask for it in your ECOHELP ticket.
    Click **Next**.
1. On the **Set up administrator account** page, populate the following fields:
    - **Full name**: any full name of the admin user
    - **Email Address**: email address of the admin user
    - **Username**: admin _(recommended)_
    - **Password**: admin _(recommended)_
    - **Confirm Password**: admin _(recommended)_
    Click **Next**.
1. On the **Set up email notifications** page, configure your email notifications, and then click **Finish**.
1. On the first page of the welcome setup select **English (United States)** language. Other languages are not supported by the toolkit.
1. After going through the welcome setup, click **Create new project** to create a new project.

---

### <a id="preloading"></a>6. Preloading your Jira Service Management deployment with an enterprise-scale dataset

Data dimensions and values for an enterprise-scale dataset are listed and described in the following table.

| Data dimensions | Value for an enterprise-scale dataset |
| --------------- | ------------------------------------- |
| Attachments | ~2 000 000 |
| Comments | ~2 000 000 |
| Components  | ~1 500 |
| Custom fields | ~400 |
| Organizations | ~300 |
| Requests | ~1 000 000 |
| Projects | 200 |
| Screen schemes | ~500 |
| Screens | ~3000 |
| Users | ~21 000 |
| Workflows | ~700 |
| Insight Schemas | ~ 6 |
| Insight Object types | ~ 50 |
| Insight Schema objects | ~ 1 000 000 |

{{% note %}}
All the datasets use the standard `admin`/`admin` credentials.
{{% /note %}}

#### Pre-loading the dataset is a three-step process:

1. [Importing the main dataset](#importingdataset). To help you out, we provide an enterprise-scale dataset you can import either via the [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/populate_db.sh) script or restore from xml backup file.
1. [Restoring attachments](#copyingattachments). We also provide attachments, which you can pre-load via an [upload_attachments.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/upload_attachments.sh) script.
1. [Re-indexing Jira Data Center](#reindexing). For more information, go to [Re-indexing Jira](https://confluence.atlassian.com/adminjiraserver/search-indexing-938847710.html).

The following subsections explain each step in greater detail.

#### <a id="importingdataset"></a> Importing the main dataset

You can load this dataset directly into the database (via a [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/populate_db.sh) script), or import it via XML.  

##### Option 1 (recommended): Loading the dataset via populate_db.sh script (~40 min)


To populate the database with SQL:

1. In the AWS console, go to **Services** > **EC2** > **Instances**.
1. On the **Description** tab, do the following:
    - Copy the _Public IP_ of the Bastion instance.
    - Copy the _Private IP_ of the Jira Service Management node instance.
1. Using SSH, connect to the Jira Service Management node via the Bastion instance:

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
1. Download the [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/populate_db.sh) script and make it executable:

    ``` bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/jira/populate_db.sh && chmod +x populate_db.sh
    ```
1. Review the following `Variables section` of the script:

    ``` bash
    DB_CONFIG="/var/atlassian/application-data/jira/dbconfig.xml"
    JIRA_DB_NAME="jira"
    JIRA_DB_USER="postgres"
    JIRA_DB_PASS="Password1!"
    # JSM section
    JIRA_CURRENT_DIR="/opt/atlassian/jira-servicedesk/current"
    JIRA_SETENV_FILE="${JIRA_CURRENT_DIR}/bin/setenv.sh"
    JIRA_VERSION_FILE="/media/atl/jira/shared/jira-servicedesk.version"
    ```
1. Run the script:

    ``` bash
    ./populate_db.sh --jsm 2>&1 | tee -a populate_db.log
    ```

{{% note %}}
Do not close or interrupt the session. It will take about 40 min to restore SQL database. When SQL restoring is finished, an admin user will have `admin`/`admin` credentials.

In case of a failure, check the `Variables` section and run the script one more time.
{{% /note %}}

##### Option 2: Loading the dataset through XML import (~4 hours)

We recommend that you only use this method if you are having problems with the [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/populate_db.sh) script.

1. In the AWS console, go to **Services** > **EC2** > **Instances**.
1. On the **Description** tab, do the following:
    - Copy the _Public IP_ of the Bastion instance.
    - Copy the _Private IP_ of the Jira Service Management node instance.
1. Using SSH, connect to the Jira Service Management node via the Bastion instance:

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
1. Download the xml_backup.zip file corresponding to your Jira Service Management version.

    ``` bash
    JSM_VERSION=$(sudo su jira -c "cat /media/atl/jira/shared/jira-servicedesk.version")
    sudo su jira -c "wget https://centaurus-datasets.s3.amazonaws.com/jsm/${JSM_VERSION}/large/xml_backup.zip -O /media/atl/jira/shared/import/xml_backup.zip"
    ```
1. Log in as a user with the **Jira System Administrators** [global permission](https://confluence.atlassian.com/adminjiraserver/managing-global-permissions-938847142.html).
1. Go to **![cog icon](/platform/marketplace/images/cog.png) &gt; System &gt; Restore System.** from the menu.
1. Populate the **File name** field with `xml_backup.zip`.
1. Click **Restore** and wait until the import is completed.

#### <a id="copyingattachments"></a> Restoring attachments (~2 hours)

After [Importing the main dataset](#importingdataset), you'll now have to pre-load an enterprise-scale set of attachments.

{{% note %}}
Populate DB and restore attachments scripts could be run in parallel in separate terminal sessions to save time.
{{% /note %}}

1. Using SSH, connect to the Jira Service Management node via the Bastion instance:

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
1. Download the [upload_attachments.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/upload_attachments.sh) script and make it executable:

    ``` bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/jira/upload_attachments.sh && chmod +x upload_attachments.sh
    ```    
1. Review the following `Variables section` of the script:

    ``` bash
    # JSM version file location
    JIRA_VERSION_FILE="/media/atl/jira/shared/jira-servicedesk.version"
    ```
1. Run the script:

    ``` bash
    ./upload_attachments.sh --jsm 2>&1 | tee -a upload_attachments.log
    ```

{{% note %}}
Do not close or interrupt the session. It will take about two hours to upload attachments to Elastic File Storage (EFS).
{{% /note %}}

#### <a id="reindexing"></a> Re-indexing Jira Service Management Data Center

For more information, go to [Re-indexing Jira](https://confluence.atlassian.com/adminjiraserver/search-indexing-938847710.html).
{{% note %}}
The re-index time for JSM 4.20.x is about ~30-50 minutes, while for JSM 5.4.x it can take significantly longer at around 110-130 minutes. This increase in re-index time is due to a known issue which affects Jira 5.4.x, and you can find more information about it in this ticket: [Re-Index: JSM 5.4.x](https://jira.atlassian.com/browse/JRASERVER-74787).
{{% /note %}}


1. Log in as a user with the **Jira System Administrators** [global permission](https://confluence.atlassian.com/adminjiraserver/managing-global-permissions-938847142.html).
1. Go to **![cog icon](/platform/marketplace/images/cog.png) &gt; System &gt; Indexing**.
1. Select the **Full re-index** option.
1. Click **Re-Index** and wait until re-indexing is completed.
1. **Take a screenshot of the acknowledgment screen** displaying the re-index time and Lucene index timing.
1. Attach the screenshot to your ECOHELP ticket.

Jira Service Management will be unavailable for some time during the re-indexing process. When finished, the **Acknowledge** button will be available on the re-indexing page.

---

#### <a id="indexrecovery"></a> Index Recovery (~15 min, only for JSM versions 5.0.x and below. For JSM 5.1.0+ skip this step.) 

1. Log in as a user with the **Jira System Administrators** [global permission](https://confluence.atlassian.com/adminjiraserver/managing-global-permissions-938847142.html).
2. Go to **![cog icon](/platform/marketplace/images/cog.png) &gt; System &gt; Indexing**.
3. In the **Index Recovery** click **Edit Settings**.
4. Set the recovery index schedule to 5min ahead of the current server time.
5. Wait ~10min until the index snapshot is created.

Jira Service Management will be unavailable for some time during the index recovery process.

6. Using SSH, connect to the Jira Service Management node via the Bastion instance:

    For Linux or MacOS run following commands in terminal (for Windows use [Git Bash](https://git-scm.com/downloads) terminal):
    
    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NODE_IP=node_private_ip
    export SSH_OPTS1='-o ServerAliveInterval=60'
    export SSH_OPTS2='-o ServerAliveCountMax=30'
    ssh ${SSH_OPTS1} ${SSH_OPTS2} -o "proxycommand ssh -W %h:%p ${SSH_OPTS1} ${SSH_OPTS2} ec2-user@${BASTION_IP}" ec2-user@${NODE_IP}
    ```
7. Once you're in the node, run command corresponding to your Jira Service Management version:
   
   
   **JSM 5**
   ```bash
    sudo su -c "du -sh  /media/atl/jira/shared/caches/indexesV2/snapshots/IndexSnapshot*" | tail -1
   ```
   **JSM 4**
   ```bash
    sudo su -c "du -sh  /media/atl/jira/shared/export/indexsnapshots/IndexSnapshot*" | tail -1
   ```
   
8. The snapshot size and name will be shown in the console output.

{{% note %}}
Please note that the snapshot size must be around 2GB or larger.
{{% /note %}}

---
{{% note %}}
After [Preloading your Jira Service Management deployment with an enterprise-scale dataset](#preloading), the admin user will have `admin`/`admin` credentials.
It's recommended to change default password from UI account page for security reasons.
{{% /note %}}
---

### <a id="executionhost"></a>7. Setting up an execution environment

For generating performance results suitable for Marketplace approval process use dedicated execution environment. This is a separate AWS EC2 instance to run the toolkit from. Running the toolkit from a dedicated instance but not from a local machine eliminates network fluctuations and guarantees stable CPU and memory performance.

1. Go to GitHub and create a fork of [dc-app-performance-toolkit](https://github.com/atlassian/dc-app-performance-toolkit).
2. Clone the fork locally, then edit the `jsm.yml` configuration file. Set enterprise-scale Jira Service Management Data Center parameters
3. In case your application relays or extends the functionality of **Insight**. Make sure to set `True` next to the `insight` variable.

{{% warning %}}
Do not push to the fork real `application_hostname`, `admin_login` and `admin_password` values for security reasons.
Instead, set those values directly in `.yml` file on execution environment instance.
{{% /warning %}}

   ``` yaml
       application_hostname: test_jsm_instance.atlassian.com   # Jira Service Management DC hostname without protocol and port e.g. test-jsm.atlassian.com or localhost
       application_protocol: http                # http or https
       application_port: 80                      # 80, 443, 8080, 2990, etc
       secure: True                              # set False to allow insecure connections, e.g. when using self-signed SSL certificate
       application_postfix:                      # set to empty for CloudFromation deploymente.g. /jira in case of url like http://localhost:2990/jira
       admin_login: admin
       admin_password: admin
       load_executor: jmeter                     # jmeter and locust are supported. jmeter by default.
       concurrency_agents: 50                    # number of concurrent virtual agents for jmeter or locust scenario
       concurrency_customers: 150                # number of concurrent virtual customers for jmeter or locust scenario
       test_duration: 45m
       ramp-up: 3m                               # time to spin all concurrent users
       total_actions_per_hour_agents: 5000       # number of total JMeter/Locust actions per hour
       total_actions_per_hour_customers: 15000   # number of total JMeter/Locust actions per hour
       insight: False                            # Set True to enable Insight specific tests
       
   ```  

1. Push your changes to the forked repository.
1. [Launch AWS EC2 instance](https://console.aws.amazon.com/ec2/). 
   * OS: select from Quick Start `Ubuntu Server 22.04 LTS`.
   * Instance type: [`c5.2xlarge`](https://aws.amazon.com/ec2/instance-types/c5/)
   * Storage size: `30` GiB
1. Connect to the instance using [SSH](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html) or the [AWS Systems Manager Sessions Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html).

   ```bash
   ssh -i path_to_pem_file ubuntu@INSTANCE_PUBLIC_IP
   ```

1. Install [Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository). Setup manage Docker as a [non-root user](https://docs.docker.com/engine/install/linux-postinstall).
1. Connect to the AWS EC2 instance and clone forked repository.

{{% note %}}
At this stage app-specific actions are not needed yet. Use code from `master` branch with your `jsm.yml` changes.
{{% /note %}}

You'll need to run the toolkit for each [test scenario](#testscenario) in the next section.

---

### <a id="testscenario"></a>8. Running the test scenarios from execution environment against enterprise-scale Jira Service Management Data Center

Using the Data Center App Performance Toolkit for [Performance and scale testing your Data Center app](/platform/marketplace/developing-apps-for-atlassian-data-center-products/) involves two test scenarios:

- [Performance regression](#testscenario1)
- [Scalability testing](#testscenario2)

Each scenario will involve multiple test runs. The following subsections explain both in greater detail.

#### <a id="testscenario1"></a> Scenario 1: Performance regression

This scenario helps to identify basic performance issues without a need to spin up a multi-node Jira Service Management DC. Make sure the app does not have any performance impact when it is not exercised.

##### <a id="regressionrun1"></a> Run 1 (~50 min)

To receive performance baseline results **without** an app installed:

1. Use SSH to connect to execution environment.
1. Run toolkit with docker from the execution environment instance:

    ``` bash
    cd dc-app-performance-toolkit
    docker run --pull=always --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt jsm.yml
    ```

1. View the following main results of the run in the `dc-app-performance-toolkit/app/results/jsm/YY-MM-DD-hh-mm-ss` folder:
    - `results_summary.log`: detailed run summary
    - `results.csv`: aggregated .csv file with all actions and timings
    - `bzt.log`: logs of the Taurus tool execution
    - `jmeter.*`: logs of the JMeter tool execution
    - `pytest.*`: logs of Pytest-Selenium execution

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps. For an enterprise-scale environment run, the acceptable success rate for actions is 95% and above.
{{% /note %}}

##### <a id="regressionrun2"></a> Run 2 (~50 min + Lucene Index timing test)

If you are submitting a Jira Service Management app, you are required to conduct a Lucene Index timing test. This involves conducting a foreground re-index on a single-node Data Center deployment (with your app installed) and a dataset that has 1M issues.

{{% note %}}
The re-index time for JSM 4.20.x is about ~30-50 minutes, while for JSM 5.4.x it can take significantly longer at around 110-130 minutes. This increase in re-index time is due to a known issue which affects Jira 5.4.x, and you can find more information about it in this ticket: [Re-Index: JSM 5.4.x](https://jira.atlassian.com/browse/JRASERVER-74787).
{{% /note %}}

{{% note %}}
If your Amazon RDS DB instance class is lower than `db.m5.xlarge` it is required to wait ~2 hours after previous reindex finish before starting a new one.
{{% /note %}}

**Benchmark your re-index time with your app installed:**

1. Install the app you want to test.
1. Setup app license.
1. Go to **![cog icon](/platform/marketplace/images/cog.png) &gt; System &gt; Indexing**.
1. Select the **Full re-index** option.
1. Click **Re-Index** and wait until re-indexing is completed.
1. **Take a screenshot of the acknowledgment screen** displaying the re-index time and Lucene index timing.
1. Attach the screenshot to your ECOHELP ticket.

**Performance results generation with the app installed:**

1. Run toolkit with docker from the execution environment instance:

   ``` bash
   cd dc-app-performance-toolkit
   docker run --pull=always --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt jsm.yml
   ```

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps. For an enterprise-scale environment run, the acceptable success rate for actions is 95% and above.
{{% /note %}}


##### Generating a performance regression report

To generate a performance regression report:  

1. Use SSH to connect to execution environment.
1. Allow current user (for execution environment default user is `ubuntu`) to access Docker generated reports:
   ``` bash
   sudo chown -R ubuntu:ubuntu /home/ubuntu/dc-app-performance-toolkit/app/results
   ```
1. Install and activate the `virtualenv` as described in `dc-app-performance-toolkit/README.md`
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

For many apps and extensions to Atlassian products, there should not be a significant performance difference between operating on a single node or across many nodes in Jira Service Management DC deployment. To demonstrate performance impacts of operating your app at scale, we recommend testing your Jira Service Management DC app in a cluster.


###### <a id="run3"></a> Run 3 (~50 min)

To receive scalability benchmark results for one-node Jira Service Management DC **with** app-specific actions:

1. Apply app-specific code changes to a new branch of forked repo.
1. Use SSH to connect to execution environment.
1. Pull cloned fork repo branch with app-specific actions.
1. Run toolkit with docker from the execution environment instance:

   ``` bash
   cd dc-app-performance-toolkit
   docker run --pull=always --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt jsm.yml
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

To receive scalability benchmark results for two-node Jira Service Management DC **with** app-specific actions:

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

5. Log in as a user with the **Jira System Administrators** [global permission](https://confluence.atlassian.com/adminjiraserver/managing-global-permissions-938847142.html). 
6. Go to **![cog icon](/platform/marketplace/images/cog.png) &gt; System &gt; Clustering** and check there is expected number of nodes with node status `ACTIVE` and application status `RUNNING`. To make sure that Jira Service Management index successfully synchronized to the second node.

{{% warning %}}
In case if index synchronization is failed by some reason (e.g. application status is `MAINTENANCE`) follow those steps:
   1. Get back and go through  **[Index Recovery steps](#indexrecovery)**. 
   2. Proceed to AWS console, go to EC2 > Instances > Select problematic node > Instances state >Terminate instance.
   3. Wait until the new node will be recreated by ASG, the index should be picked up by a new node automatically.
{{% /warning %}}
   
7. Run toolkit with docker from the execution environment instance:

   ``` bash
   cd dc-app-performance-toolkit
   docker run --pull=always --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt jsm.yml
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

To receive scalability benchmark results for four-node Jira Service Management DC with app-specific actions:

1. Scale your Jira Service Management Data Center deployment to 3 nodes as described in [Run 4](#run4).
1. Check Index is synchronized to the new node #3 the same way as in [Run 4](#run4).
1. Scale your Jira Service Management Data Center deployment to 4 nodes as described in [Run 4](#run4).
1. Check Index is synchronized to the new node #4 the same way as in [Run 4](#run4).
1. Run toolkit with docker from the execution environment instance:

   ``` bash
   cd dc-app-performance-toolkit
   docker run --pull=always --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt jsm.yml
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
1. Once completed, in the `./reports` folder, you will be able to review action timings on Jira Service Management Data Center with different numbers of nodes. If you see a significant variation in any action timings between configurations, we recommend taking a look into the app implementation to understand the root cause of this delta.

{{% warning %}}
After completing all your tests, delete your Jira Service Management Data Center stacks.
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
