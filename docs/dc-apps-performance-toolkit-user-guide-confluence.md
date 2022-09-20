---
title: "Data Center App Performance Toolkit User Guide For Confluence"
platform: platform
product: marketplace
category: devguide
subcategory: build
date: "2022-07-25"
---
# Data Center App Performance Toolkit User Guide For Confluence

This document walks you through the process of testing your app on Confluence using the Data Center App Performance Toolkit. These instructions focus on producing the required [performance and scale benchmarks for your Data Center app](/platform/marketplace/dc-apps-performance-and-scale-testing/).

In this document, we cover the use of the Data Center App Performance Toolkit on two types of environments:

**[Development environment](#mainenvironmentdev)**: Confluence Data Center environment for a test run of Data Center App Performance Toolkit and development of [app-specific actions](#appspecificactions). We recommend you use the [AWS Quick Start for Confluence Data Center](https://aws.amazon.com/quickstart/architecture/confluence/) with the parameters prescribed here.

1. [Set up a development environment Confluence Data Center on AWS](#devinstancesetup).
2. [Create a dataset for the development environment](#devdataset).
3. [Run toolkit on the development environment locally](#devtestscenario).
4. [Develop and test app-specific actions locally](#devappaction).

**[Enterprise-scale environment](#mainenvironmententerprise)**: Confluence Data Center environment used to generate Data Center App Performance Toolkit test results for the Marketplace approval process. Preferably, use the [AWS Quick Start for Confluence Data Center](https://aws.amazon.com/quickstart/architecture/confluence/) with the parameters prescribed below. These parameters provision larger, more powerful infrastructure for your Confluence Data Center.

5. [Set up an enterprise-scale environment Confluence Data Center on AWS](#instancesetup).
6. [Load an enterprise-scale dataset on your Confluence Data Center deployment](#preloading).
7. [Set up an execution environment for the toolkit](#executionhost).
8. [Running the test scenarios from execution environment against enterprise-scale Confluence Data Center](#testscenario).

---

## <a id="mainenvironmentdev"></a>Development environment

Running the tests in a development environment helps familiarize you with the toolkit. It'll also provide you with a lightweight and less expensive environment for developing. Once you're ready to generate test results for the Marketplace Data Center Apps Approval process, run the toolkit in an **enterprise-scale environment**.

### <a id="devinstancesetup"></a>1. Setting up Confluence Data Center development environment

We recommend that you set up development environment using the [AWS Quick Start for Confluence Data Center](https://aws.amazon.com/quickstart/architecture/confluence/) (**How to deploy** tab). All the instructions on this page are optimized for AWS. If you already have an existing Confluence Data Center environment, you can also use that too (if so, skip to [Create a dataset for the development environment](#devdataset)).


#### Using the AWS Quick Start for Confluence

If you are a new user, perform an end-to-end deployment. This involves deploying Confluence into a _new_ ASI:

Navigate to **[AWS Quick Start for Confluence Data Center](https://aws.amazon.com/quickstart/architecture/confluence/) &gt; How to deploy** tab **&gt; Deploy into a new ASI** link.

If you have already deployed the ASI separately by using the [ASI Quick Start](https://aws.amazon.com/quickstart/architecture/atlassian-standard-infrastructure/)ASI Quick Start or by deploying another Atlassian product (Jira, Bitbucket, or Confluence Data Center development environment) with ASI, deploy Confluence into your existing ASI:

Navigate to **[AWS Quick Start for Confluence Data Center](https://aws.amazon.com/quickstart/architecture/confluence/) &gt; How to deploy** tab **&gt; Deploy into your existing ASI** link.

{{% note %}}
You are responsible for the cost of AWS services used while running this Quick Start reference deployment. This Quick Start doesn't have any additional prices. See [Amazon EC2 pricing](https://aws.amazon.com/ec2/pricing/) for more detail.
{{% /note %}}

To reduce costs, we recommend you to keep your deployment up and running only during the performance runs.

#### AWS cost estimation for the development environment

AWS Confluence Data Center development environment infrastructure costs about 20 - 40$ per working week depending on such factors like region, instance type, deployment type of DB, and other.  

#### <a id="quick-start-parameters"></a> Quick Start parameters for development environment

All important parameters are listed and described in this section. For all other remaining parameters, we recommend using the Quick Start defaults.

**Confluence setup**

| Parameter | Recommended value                                                                                                                                                                                        |
| --------- |----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Collaborative editing mode | synchrony-local                                                                                                                                                                                          |
| Confluence Version | The Data Center App Performance Toolkit officially supports `7.13.7` ([Long Term Support release](https://confluence.atlassian.com/enterprise/atlassian-enterprise-releases-948227420.html)) |


**Cluster nodes**

| Parameter | Recommended value |
| --------- | ----------------- |
| Cluster node instance type | [t3.medium](https://aws.amazon.com/ec2/instance-types/t3/) (we recommend this instance type for its good balance between price and performance in testing environments) |
| Maximum number of cluster nodes | 1 |
| Minimum number of cluster nodes | 1 |
| Cluster node instance volume size | 50 |


**Database**

| Parameter | Recommended value |
| --------- | ----------------- |
| The database engine | PostgresSQL |
| The database engine version to use | 10 |
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
1. On the **Configure User Management** page, click on the **Manage users and groups within Confluence**.
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

---

### <a id="devdataset"></a>2. Generate dataset for development environment  

After creating the development environment Confluence Data Center, generate test dataset to run Data Center App Performance Toolkit:
- 1 space with 1-5 pages and 1-5 blog posts.

---

### <a id="devtestscenario"></a>3. Run toolkit on the development environment locally

{{% warning %}}
Make sure **English** language is selected as a default language on the **![cog icon](/platform/marketplace/images/cog.png) &gt; General configuration &gt; Languages** page. Other languages are **not supported** by the toolkit.
{{% /warning %}}

{{% warning %}}
Make sure **Remote API** is enabled on the **![cog icon](/platform/marketplace/images/cog.png) &gt; General configuration &gt; Further Configuration** page.
{{% /warning %}}

1. Clone [Data Center App Performance Toolkit](https://github.com/atlassian/dc-app-performance-toolkit) locally.
1. Follow the [README.md](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/README.md) instructions to set up toolkit locally.
1. Navigate to `dc-app-performance-toolkit/app` folder.
1. Open the `confluence.yml` file and fill in the following variables:
    - `application_hostname`: your_dc_confluence_instance_hostname without protocol.
    - `application_protocol`: http or https.
    - `application_port`: for HTTP - 80, for HTTPS - 443, 8080, 1990 or your instance-specific port.
    - `secure`: True or False. Default value is True. Set False to allow insecure connections, e.g. when using self-signed SSL certificate.
    - `application_postfix`: it is empty by default; e.g., /confluence for url like this http://localhost:1990/confluence.
    - `admin_login`: admin user username.
    - `admin_password`: admin user password.
    - `load_executor`: executor for load tests. Valid options are [jmeter](https://jmeter.apache.org/) (default) or [locust](https://locust.io/).
    - `concurrency`: `2` - number of concurrent JMeter/Locust users.
    - `test_duration`: `5m` - duration of the performance run.
    - `ramp-up`: `5s` - amount of time it will take JMeter or Locust to add all test users to test execution.
    - `total_actions_per_hour`: `2000` - number of total JMeter/Locust actions per hour.
    - `WEBDRIVER_VISIBLE`: visibility of Chrome browser during selenium execution (False is by default).

1. Run bzt.

    ``` bash
    bzt confluence.yml
    ```

1. Review the resulting table in the console log. All JMeter/Locust and Selenium actions should have 95+% success rate.  
In case some actions does not have 95+% success rate refer to the following logs in `dc-app-performance-toolkit/app/results/confluence/YY-MM-DD-hh-mm-ss` folder:

    - `results_summary.log`: detailed run summary
    - `results.csv`: aggregated .csv file with all actions and timings
    - `bzt.log`: logs of the Taurus tool execution
    - `jmeter.*`: logs of the JMeter tool execution
    - `locust.*`: logs of the Locust tool execution (in case you use Locust as load_executor in confluence.yml)
    - `pytest.*`: logs of Pytest-Selenium execution

{{% warning %}}
Do not proceed with the next step until you have all actions 95+% success rate. Ask [support](#support) if above logs analysis did not help.
{{% /warning %}}

---

### <a id="devappaction"></a>4. Develop and test app-specific action locally
Data Center App Performance Toolkit has its own set of default test actions for Confluence Data Center: JMeter/Locust and Selenium for load and UI tests respectively.     

**App-specific action** - action (performance test) you have to develop to cover main use cases of your application. Performance test should focus on the common usage of your application and not to cover all possible functionality of your app. For example, application setup screen or other one-time use cases are out of scope of performance testing.

1. Define main use case of your app. Usually it is one or two main app use cases.
1. Your app adds new UI elements in Confluence Data Center - Selenium app-specific action has to be developed.
1. Your app introduces new endpoint or extensively calls existing Confluence Data Center API - JMeter/Locust app-specific actions has to be developed.  
JMeter and Locust actions are interchangeable, so you could select the tool you prefer:

- JMeter - UI-based [performance tool](https://jmeter.apache.org/).
- Locust - code-based (Python requests library) [performance tool](https://locust.io/).


{{% note %}}
We strongly recommend developing your app-specific actions on the development environment to reduce AWS infrastructure costs.
{{% /note %}}


#### Custom dataset
You can filter your own app-specific pages/blog posts for your app-specific actions.

1. Create app-specific pages/blog posts that have specific anchor in title, e.g. *AppPage* anchor and pages titles like *AppPage1*, *AppPage2*, *AppPage3*.
1. Go to the search page of your Confluence Data Center - `CONFLUENCE_URL/dosearchsite.action?queryString=` (Confluence versions 6.X and below) or just click to search field in UI (Confluence versions 7.X and higher).
1. Write [CQL](https://confluence.atlassian.com/doc/confluence-search-syntax-158720.html) that filter just your pages or blog posts from step 1, e.g. `title ~ 'AppPage*'`.
1. Edit Confluence configuration file `dc-app-performance-toolkit/app/confluence.yml`:  
    - `custom_dataset_query:` CQL from step 3.

Next time when you run toolkit, custom dataset pages will be stored to the `dc-app-performance-toolkit/app/datasets/confluence/custom_pages.csv` with columns: `page_id`, `space_key`.

#### Example of app-specific Selenium action development with custom dataset  
You develop an app that adds additional UI elements to Confluence pages or blog posts. In this case, you should develop Selenium app-specific action:

1. Create app-specific Confluence pages with *AppPagee* anchor in title: *AppPage1*, *AppPage2*, *AppPage3, etc.
2. Go to the search page of your Confluence Data Center - `CONFLUENCE_URL/dosearchsite.action?queryString=` (Confluence versions 6.X and below) or just click to search field in UI (Confluence versions 7.X and higher) and check if CQL is correct: `title ~ 'AppPage*'`.
3. Edit `dc-app-performance-toolkit/app/confluence.yml` configuration file and set `custom_dataset_query: "title ~ 'AppPage*'"`.
4. Extend example of app-specific action in `dc-app-performance-toolkit/app/extension/confluence/extension_ui.py`.  
[Code example.](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/extension/confluence/extension_ui.py)
So, our test has to open page or blog post with app-specific UI element and measure time to load of this app-specific page or blog post.
5. If you need to run `app_speicifc_action` as specific user uncomment `app_specific_user_login` function in [code example](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/extension/confluence/extension_ui.py). Note, that in this case `test_1_selenium_custom_action` should follow just before `test_2_selenium_z_log_out` action.
6. In `dc-app-performance-toolkit/app/selenium_ui/confluence_ui.py`, review and uncomment the following block of code to make newly created app-specific actions executed:
``` python
# def test_1_selenium_custom_action(confluence_webdriver, confluence_datasets, confluence_screen_shots):
#     extension_ui.app_specific_action(confluence_webdriver, confluence_datasets)
```

7. Run toolkit with `bzt confluence.yml` command to ensure that all Selenium actions including `app_specific_action` are successful.

#### Example of app-specific Locust/JMeter action development

You develop an app that introduces new GET and POST endpoints in Confluence Data Center. In this case, you should develop Locust or JMeter app-specific action.

**Locust app-specific action development example**

1. Extend example of app-specific action in `dc-app-performance-toolkit/app/extension/confluence/extension_locust.py`, so that test will call the endpoint with GET request, parse response use these data to call another endpoint with POST request and measure response time.  
[Code example.](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/extension/confluence/extension_locust.py)
1. In `dc-app-performance-toolkit/app/confluence.yml` set `load_executor: locust` to make `locust` as load executor.
1. Set desired execution percentage for `standalone_extension`. Default value is `0`, which means that `standalone_extension` action will not be executed. Locust uses actions percentage as relative [weights](https://docs.locust.io/en/stable/writing-a-locustfile.html#weight-attribute), so if `some_action: 10` and `standalone_extension: 20` that means that `standalone_extension` will be called twice more.  
Set `standalone_extension` weight in accordance with the expected frequency of your app use case compared with other base actions.
1. App-specific tests could be run (if needed) as a specific user. Use `@run_as_specific_user(username='specific_user_username', password='specific_user_password')` decorator for that.
1. Run toolkit with `bzt confluence.yml` command to ensure that all Locust actions including `app_specific_action` are successful.

**JMeter app-specific action development example**

1. Check that `confluence.yml` file has correct settings of `application_hostname`, `application_protocol`, `application_port`, `application_postfix`, etc.
1. Set desired execution percentage for `standalone_extension`. Default value is `0`, which means that `standalone_extension` action will not be executed. 
For example, for app-specific action development you could set percentage of `standalone_extension` to 100 and for all other actions to 0 - this way only `login_and_view_dashboard` and `standalone_extension` actions would be executed.
1. Navigate to `dc-app-performance-toolkit/app` folder and run from virtualenv(as described in `dc-app-performance-toolkit/README.md`):
    
    ```python util/jmeter/start_jmeter_ui.py --app confluence```
    
1. Open `Confluence` thread group > `actions per login` and navigate to `standalone_extension`
![Confluence JMeter standalone extension](/platform/marketplace/images/confluence-standalone-extenstion.png)
1. Add GET `HTTP Request`: right-click to `standalone_extension` > `Add` > `Sampler` `HTTP Request`, chose method GET and set endpoint in Path.
![Confluence JMeter standalone GET](/platform/marketplace/images/confluence-standalone-get-request.png)
1. Add `Regular Expression Extractor`: right-click to to newly created `HTTP Request` > `Add` > `Post processor` > `Regular Expression Extractor`
![Confluence JMeter standalone regexp](/platform/marketplace/images/confluence-standalone-regexp.png)
1. Add `Response Assertion`: right-click to newly created `HTTP Request` > `Add` > `Assertions` > `Response Assertion` and add assertion with `Contains`, `Matches`, `Equals`, etc types.
![Confluence JMeter standalone assertions](/platform/marketplace/images/confluence-standalone-assertions.png)
1. Add POST `HTTP Request`: right-click to `standalone_extension` > `Add` > `Sampler` `HTTP Request`, chose method POST, set endpoint in Path and add Parameters or Body Data if needed.
1. Right-click on `View Results Tree` and enable this controller.
1. Click **Start** button and make sure that `login_and_view_dashboard` and `standalone_extension` are successful.
1. Right-click on `View Results Tree` and disable this controller. It is important to disable `View Results Tree` controller before full-scale results generation.
1. Click **Save** button.
1. To make `standalone_extension` executable during toolkit run edit `dc-app-performance-toolkit/app/confluence.yml` and set execution percentage of `standalone_extension` accordingly to your use case frequency.
1. App-specific tests could be run (if needed) as a specific user. In the `standalone_extension` uncomment `login_as_specific_user` controller. Navigate to the `username:password` config element and update values for `app_specific_username` and `app_specific_password` names with your specific user credentials. Also make sure that you located your app-specific tests between `login_as_specific_user` and `login_as_default_user_if_specific_user_was_loggedin` controllers.   
1. Run toolkit to ensure that all JMeter actions including `standalone_extension` are successful.

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

{{% warning %}}
App-specific actions are required. Do not proceed with the next step until you have completed app-specific actions development and got successful results from toolkit run.
{{% /warning %}}


---
## <a id="mainenvironmententerprise"></a> Enterprise-scale environment

After adding your custom app-specific actions, you should now be ready to run the required tests for the Marketplace Data Center Apps Approval process. To do this, you'll need an **enterprise-scale environment**.

### <a id="instancesetup"></a>5. Setting up Confluence Data Center enterprise-scale environment

We recommend that you use the [AWS Quick Start for Confluence Data Center](https://aws.amazon.com/quickstart/architecture/confluence/) (**How to deploy** tab) to deploy a Confluence Data Center testing environment. This Quick Start will allow you to deploy Confluence Data Center with a new [Atlassian Standard Infrastructure](https://aws.amazon.com/quickstart/architecture/atlassian-standard-infrastructure/) (ASI) or into an existing one.

The ASI is a Virtual Private Cloud (VPC) consisting of subnets, NAT gateways, security groups, bastion hosts, and other infrastructure components required by all Atlassian applications, and then deploys Confluence into this new VPC. Deploying Confluence with a new ASI takes around 50 minutes. With an existing one, it'll take around 30 minutes.

### Using the AWS Quick Start for Confluence

If you are a new user, perform an end-to-end deployment. This involves deploying Confluence into a _new_ ASI:

Navigate to **[AWS Quick Start for Confluence Data Center](https://aws.amazon.com/quickstart/architecture/confluence/) &gt; How to deploy** tab **&gt; Deploy into a new ASI** link.

If you have already deployed the ASI separately by using the [ASI Quick Start](https://aws.amazon.com/quickstart/architecture/atlassian-standard-infrastructure/)ASI Quick Start or by deploying another Atlassian product (Jira, Bitbucket, or Confluence Data Center development environment) with ASI, deploy Confluence into your existing ASI:

Navigate to **[AWS Quick Start for Confluence Data Center](https://aws.amazon.com/quickstart/architecture/confluence/) &gt; How to deploy** tab **&gt; Deploy into your existing ASI** link.

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
| One Node Confluence DC | 0.8 - 1.1 |
| Two Nodes Confluence DC | 1.2 - 1.7 |
| Four Nodes Confluence DC | 2.0 - 3.0 |

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

#### Quick Start parameters

All important parameters are listed and described in this section. For all other remaining parameters, we recommend using the Quick Start defaults.

**Confluence setup**

| Parameter | Recommended value                                                                                                                                                                                         |
| --------- |-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Collaborative editing mode | synchrony-local                                                                                                                                                                                           |
| Confluence Version | The Data Center App Performance Toolkit officially supports `7.13.7` ([Long Term Support release](https://confluence.atlassian.com/enterprise/atlassian-enterprise-releases-948227420.html)) |

**Cluster nodes**

| Parameter | Recommended Value |
| ----------| ----------------- |
| Cluster node instance type | [m5.2xlarge](https://aws.amazon.com/ec2/instance-types/m5/) |
| Maximum number of cluster nodes | 1 |
| Minimum number of cluster nodes | 1 |
| Cluster node instance volume size | 200 |

We recommend [m5.2xlarge](https://aws.amazon.com/ec2/instance-types/m5/) to strike the balance between cost and hardware we see in the field for our enterprise customers. More info could be found in public [recommendations](https://confluence.atlassian.com/enterprise/infrastructure-recommendations-for-enterprise-confluence-instances-on-aws-965544795.html).

The Data Center App Performance Toolkit framework is also set up for concurrency we expect on this instance size. As such, underprovisioning will likely show a larger performance impact than expected.

**Database**

| Parameter | Recommended Value |
| --------- | ----------------- |
| The database engine | PostgresSQL |
| The database engine version to use | 10 |
| Database instance class | [db.m5.xlarge](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html#Concepts.DBInstanceClass.Summary) |
| RDS Provisioned IOPS | 1000 |
| Master (admin) password | Password1! |
| Enable RDS Multi-AZ deployment | false |
| Application user database password | Password1! |
| Database storage | 200 |

{{% note %}}
The **Master (admin) password** will be used later when restoring the SQL database dataset. If password value is not set to default, you'll need to change `DB_PASS` value manually in the restore database dump script (later in [Preloading your Confluence deployment with an enterprise-scale dataset](#preloading)).
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

**Application tuning**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Catalina options | -Dreindex.thread.count=8 -Dreindex.attachments.thread.count=8 -Dconfluence.reindex.documents.to.pop=600 |

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
1. On the **Configure User Management** page, click on the **Manage users and groups within Confluence**.
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
---

### <a id="preloading"></a>6. Preloading your Confluence deployment with an enterprise-scale dataset

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
1. Download the [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/confluence/populate_db.sh) script and make it executable:

    ``` bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/confluence/populate_db.sh && chmod +x populate_db.sh
    ```
1. Review the following `Variables section` of the script:

    ``` bash
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
    ./populate_db.sh 2>&1 | tee -a populate_db.log
    ```

{{% note %}}
Do not close or interrupt the session. It will take some time to restore SQL database. When SQL restoring is finished, an admin user will have `admin`/`admin` credentials.

In case of a failure, check the `Variables` section and run the script one more time.
{{% /note %}}

### <a id="copyingattachments"></a> Restoring attachments (~3 hours)

After [Importing the main dataset](#importingdataset), you'll now have to pre-load an enterprise-scale set of attachments.

{{% note %}}
Populate DB and restore attachments scripts could be run in parallel in separate terminal sessions to save time.
{{% /note %}}

1. Using SSH, connect to the Confluence node via the Bastion instance:

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
    ./upload_attachments.sh 2>&1 | tee -a upload_attachments.log
    ```

{{% note %}}
Do not close or interrupt the session. It will take some time to upload attachments to Elastic File Storage (EFS).
{{% /note %}}

### <a id="reindexing"></a> Re-indexing Confluence Data Center (~2-3 hours)

For more information, go to [Re-indexing Confluence](https://confluence.atlassian.com/doc/content-index-administration-148844.html).

Index process is triggered automatically after `polulate_db.sh` script execution.

For Confluence **7.4.x**:

1. Log in as a user with the **Confluence System Administrators** [global permission](https://confluence.atlassian.com/doc/global-permissions-overview-138709.html).
1. Go to **![cog icon](/platform/marketplace/images/cog.png) &gt; General Configuration &gt; Content Indexing**.
1. Wait until re-indexing is completed.

For Confluence **7.13.x**:

1. Using SSH, connect to the Confluence node via the Bastion instance:

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
1. Download the [index-wait-till-finished.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/confluence/index-wait-till-finished.sh) script and make it executable:

    ``` bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/confluence/index-wait-till-finished.sh && chmod +x index-wait-till-finished.sh
    ```
1. Run the script:

    ``` bash
    ./index-wait-till-finished.sh 2>&1 | tee -a index-wait-till-finished.log
    ```

### <a id="index-snapshot"></a> Create Index Snapshot (~30 min)

For more information, go to [Administer your Data Center search index](https://confluence.atlassian.com/doc/administer-your-data-center-search-index-879956107.html).

1. Log in as a user with the **Confluence System Administrators** [global permission](https://confluence.atlassian.com/doc/global-permissions-overview-138709.html).
1. Create any new page with a random content (without a new page index snapshot job will not be triggered).
1. Go to **![cog icon](/platform/marketplace/images/cog.png) &gt; General Configuration &gt; Scheduled Jobs**.
1. Find **Clean Journal Entries** job and click **Run**.
1. Make sure that Confluence index snapshot was created. To do that, use SSH to connect to the Confluence node via Bastion (where `NODE_IP` is the IP of the node):

    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NODE_IP=node_private_ip
    export SSH_OPTS1='-o ServerAliveInterval=60'
    export SSH_OPTS2='-o ServerAliveCountMax=30'
    ssh ${SSH_OPTS1} ${SSH_OPTS2} -o "proxycommand ssh -W %h:%p ${SSH_OPTS1} ${SSH_OPTS2} ec2-user@${BASTION_IP}" ec2-user@${NODE_IP}
    ```
1. Download the [index-snapshot.sh](https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/confluence/index-snapshot.sh) file. Then, make it executable and run it:

    ```bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/confluence/index-snapshot.sh && chmod +x index-snapshot.sh
    ./index-snapshot.sh 2>&1 | tee -a index-snapshot.log
    ```
    Index snapshot creation time is about 20-30 minutes. When index snapshot is successfully created, the following will be displayed in console output:
    ```bash
    Snapshot was created successfully.
    ```

---
{{% note %}}
After [Preloading your Confluence deployment with an enterprise-scale dataset](#preloading), the admin user will have `admin`/`admin` credentials.
It's recommended to change default password from UI account page for security reasons.
{{% /note %}}
---

### <a id="executionhost"></a>7. Setting up an execution environment

For generating performance results suitable for Marketplace approval process use dedicated execution environment. This is a separate AWS EC2 instance to run the toolkit from. Running the toolkit from a dedicated instance but not from a local machine eliminates network fluctuations and guarantees stable CPU and memory performance.

1. Go to GitHub and create a fork of [dc-app-performance-toolkit](https://github.com/atlassian/dc-app-performance-toolkit).
1. Clone the fork locally, then edit the `confluence.yml` configuration file. Set enterprise-scale Confluence Data Center parameters:

{{% warning %}}
Do not push to the fork real `application_hostname`, `admin_login` and `admin_password` values for security reasons.
Instead, set those values directly in `.yml` file on execution environment instance.
{{% /warning %}}

   ``` yaml
       application_hostname: test_confluence_instance.atlassian.com   # Confluence DC hostname without protocol and port e.g. test-confluence.atlassian.com or localhost
       application_protocol: http      # http or https
       application_port: 80            # 80, 443, 8080, 2990, etc
       secure: True                    # Set False to allow insecure connections, e.g. when using self-signed SSL certificate
       application_postfix:            # e.g. /confluence in case of url like http://localhost:2990/confluence
       admin_login: admin
       admin_password: admin
       load_executor: jmeter           # jmeter and locust are supported. jmeter by default.
       concurrency: 200                # number of concurrent virtual users for jmeter or locust scenario
       test_duration: 45m
       ramp-up: 5m                     # time to spin all concurrent users
       total_actions_per_hour: 20000   # number of total JMeter/Locust actions per hour.
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

{{% note %}}
At this stage app-specific actions are not needed yet. Use code from `master` branch with your `confluence.yml` changes.
{{% /note %}}

You'll need to run the toolkit for each [test scenario](#testscenario) in the next section.

---

### <a id="testscenario"></a>8. Running the test scenarios from execution environment against enterprise-scale Confluence Data Center

Using the Data Center App Performance Toolkit for [Performance and scale testing your Data Center app](/platform/marketplace/developing-apps-for-atlassian-data-center-products/) involves two test scenarios:

- [Performance regression](#testscenario1)
- [Scalability testing](#testscenario2)

Each scenario will involve multiple test runs. The following subsections explain both in greater detail.

#### <a id="testscenario1"></a> Scenario 1: Performance regression

This scenario helps to identify basic performance issues without a need to spin up a multi-node Confluence DC. Make sure the app does not have any performance impact when it is not exercised.

##### <a id="regressionrun1"></a> Run 1 (~50 min)

To receive performance baseline results **without** an app installed:

1. Use SSH to connect to execution environment.
1. Run toolkit with docker from the execution environment instance:

    ``` bash
    cd dc-app-performance-toolkit
    docker pull atlassian/dcapt
    docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt confluence.yml
    ```

1. View the following main results of the run in the `dc-app-performance-toolkit/app/results/confluence/YY-MM-DD-hh-mm-ss` folder:
    - `results_summary.log`: detailed run summary
    - `results.csv`: aggregated .csv file with all actions and timings
    - `bzt.log`: logs of the Taurus tool execution
    - `jmeter.*`: logs of the JMeter tool execution
    - `pytest.*`: logs of Pytest-Selenium execution

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps. For an enterprise-scale environment run, the acceptable success rate for actions is 95% and above.
{{% /note %}}

##### <a id="regressionrun2"></a> Run 2 (~50 min)

To receive performance results with an app installed:

1. Install the app you want to test.
1. Setup app license.
1. Run toolkit with docker from the execution environment instance:

   ``` bash
   cd dc-app-performance-toolkit
   docker pull atlassian/dcapt
   docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt confluence.yml
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

For many apps and extensions to Atlassian products, there should not be a significant performance difference between operating on a single node or across many nodes in Confluence DC deployment. To demonstrate performance impacts of operating your app at scale, we recommend testing your Confluence DC app in a cluster.


##### <a id="run3"></a> Run 3 (~50 min)

To receive scalability benchmark results for one-node Confluence DC **with** app-specific actions:

1. Apply app-specific code changes to a new branch of forked repo.
1. Use SSH to connect to execution environment.
1. Pull cloned fork repo branch with app-specific actions.
1. Run toolkit with docker from the execution environment instance:

   ``` bash
   cd dc-app-performance-toolkit
   docker pull atlassian/dcapt
   docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt confluence.yml
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

To receive scalability benchmark results for two-node Confluence DC **with** app-specific actions:

1. In the AWS console, go to **CloudFormation > Stack details > Select your stack**.
1. On the **Update** tab, select **Use current template**, and then click **Next**.
1. Enter `2` in the **Maximum number of cluster nodes** and the **Minimum number of cluster nodes** fields.
1. Click **Next > Next > Update stack** and wait until stack is updated.
1. Confirm new node is appeared on the **![cog icon](/platform/marketplace/images/cog.png) &gt; General Configuration &gt; Clustering** page.   
1. Make sure that Confluence index successfully synchronized to the second node. To do that, use SSH to connect to the second node via Bastion (where `NODE_IP` is the IP of the second node):

    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NODE_IP=node_private_ip
    export SSH_OPTS1='-o ServerAliveInterval=60'
    export SSH_OPTS2='-o ServerAliveCountMax=30'
    ssh ${SSH_OPTS1} ${SSH_OPTS2} -o "proxycommand ssh -W %h:%p ${SSH_OPTS1} ${SSH_OPTS2} ec2-user@${BASTION_IP}" ec2-user@${NODE_IP}
    ```
1. Once you're in the second node, download the [index-sync.sh](https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/confluence/index-sync.sh) file. Then, make it executable and run it:

    ```bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/confluence/index-sync.sh && chmod +x index-sync.sh
    ./index-sync.sh 2>&1 | tee -a index-sync.log
    ```
    Index synchronizing time is about 10-30 minutes. When index synchronizing is successfully completed, the following lines will be displayed in console output:
    ```bash
    Log file: /var/atlassian/application-data/confluence/logs/atlassian-confluence.log
    Index recovery is required for main index, starting now
    main index recovered from shared home directory
    ```

1. Run toolkit with docker from the execution environment instance:

   ``` bash
   cd dc-app-performance-toolkit
   docker pull atlassian/dcapt
   docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt confluence.yml
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

To receive scalability benchmark results for four-node Confluence DC with app-specific actions:

1. Scale your Confluence Data Center deployment to 3 nodes as described in [Run 4](#run4).
1. Check Index is synchronized to the new node #3 the same way as in [Run 4](#run4).
1. Scale your Confluence Data Center deployment to 4 nodes as described in [Run 4](#run4).
1. Check Index is synchronized to the new node #4 the same way as in [Run 4](#run4).
1. Run toolkit with docker from the execution environment instance:

   ``` bash
   cd dc-app-performance-toolkit
   docker pull atlassian/dcapt
   docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt confluence.yml
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
1. Once completed, in the `./reports` folder, you will be able to review action timings on Confluence Data Center with different numbers of nodes. If you see a significant variation in any action timings between configurations, we recommend taking a look into the app implementation to understand the root cause of this delta.

{{% warning %}}
After completing all your tests, delete your Confluence Data Center stacks.
{{% /warning %}}

#### Attaching testing results to DCHELP ticket

{{% warning %}}
Do not forget to attach performance testing results to your DCHELP ticket.
{{% /warning %}}

1. Make sure you have two reports folders: one with performance profile and second with scale profile results. 
   Each folder should have `profile.csv`, `profile.png`, `profile_summary.log` and profile run result archives. Archives 
   should contain all raw data created during the run: `bzt.log`, selenium/jmeter/locust logs, .csv and .yml files, etc.
2. Attach two reports folders to your DCHELP ticket.

## <a id="support"></a> Support
In case of technical questions, issues or problems with DC Apps Performance Toolkit, contact us for support in the [community Slack](http://bit.ly/dcapt_slack) **#data-center-app-performance-toolkit** channel.
