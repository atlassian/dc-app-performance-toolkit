---
title: "Data Center App Performance Toolkit User Guide For Jira Service Management"
platform: platform
product: marketplace
category: devguide
subcategory: build
date: "2023-08-15"
---
# Data Center App Performance Toolkit User Guide For Jira Service Management

This document walks you through the process of testing your app on Jira Service Management using the Data Center App Performance Toolkit. These instructions focus on producing the required [performance and scale benchmarks for your Data Center app](/platform/marketplace/dc-apps-performance-and-scale-testing/):

If your application relays or extends the functionality of **Insight** ([What is Insight?](https://confluence.atlassian.com/servicemanagementserver/what-is-insight-1044784313.html)):

Please, make sure you have enabled Insight-specific tests in the `jsm.yml` file, by setting `True` value next to the `insight` variable.


In this document, we cover the use of the Data Center App Performance Toolkit on two types of environments:


**[Development environment](#mainenvironmentdev)**: Jira Service Management Data Center environment for a test run of Data Center App Performance Toolkit and development of [app-specific actions](#appspecificactions).

1. [Set up a development environment Jira Service Management Data Center on AWS](#devinstancesetup).
2. [Run toolkit on the development environment locally](#devtestscenario).
3. [Develop and test app-specific actions locally](#devappaction).

**[Enterprise-scale environment](#mainenvironmententerprise)**: Jira Service Management Data Center environment used to generate Data Center App Performance Toolkit test results for the Marketplace approval process.

4. [Set up an enterprise-scale environment Jira Service Management Data Center on AWS](#instancesetup).
5. [Set up an execution environment for the toolkit](#executionhost).
6. [Running the test scenarios from execution environment against enterprise-scale Jira Service Management Data Center](#testscenario).

---

## <a id="mainenvironmentdev"></a>Development environment

Running the tests in a development environment helps familiarize you with the toolkit.
It'll also provide you with a lightweight and less expensive environment for developing app-specific actions.
Once you're ready to generate test results for the Marketplace Data Center Apps Approval process,
run the toolkit in an **enterprise-scale environment**.

---

{{% note %}}
DCAPT has fully transitioned to Terraform deployment. If you still wish to use CloudFormation deployment, refer to the [Jira Service Management Data Center app testing [CloudFormation]](/platform/marketplace/dc-apps-performance-toolkit-user-guide-jsm-cf/)
{{% /note %}}

### <a id="devinstancesetup"></a>1. Setting up Jira Service Management Data Center development environment

#### AWS cost estimation for the development environment

{{% note %}}
You are responsible for the cost of AWS services used while running this Terraform deployment.
See [Amazon EC2 pricing](https://aws.amazon.com/ec2/pricing/) for more detail.
{{% /note %}}

To reduce costs, we recommend you to keep your deployment up and running only during the performance runs.
AWS Jira Service Management Data Center development environment infrastructure costs about  20 - 40$ per working week depending on such factors like region, instance type, deployment type of DB, and other.  

#### Setup Jira Service Management Data Center development environment on k8s.

{{% note %}}
Jira Service Management Data Center development environment is good for app-specific actions development.
But not powerful enough for performance testing at scale.
See [Set up an enterprise-scale environment Jira Service Management Data Center on AWS](#instancesetup) for more details.
{{% /note %}}

Below process describes how to install low-tier Jira Service Management DC with "small" dataset included:

1. Create [access keys for IAM user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey).
   {{% warning %}}
   Do not use `root` user credentials for cluster creation. Instead, [create an admin user](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-set-up.html#create-an-admin).
   {{% /warning %}}
2. Navigate to `dc-apps-peformance-toolkit/app/util/k8s` folder.
3. Set AWS access keys created in step1 in `aws_envs` file:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
4. Set **required** variables in `dcapt-small.tfvars` file:
   - `environment_name` - any name for you environment, e.g. `dcapt-jsm-small`.
   - `products` - `jira`
   - `jira_image_repository` - `atlassian/jira-servicemanagement` - make sure to select the **Jira Service Management** application.
   - `jira_license` - one-liner of valid Jira Service Management license without spaces and new line symbols.
   - `region` - AWS region for deployment. **Do not change default region (`us-east-2`). If specific region is required, contact support.**

   {{% note %}}
   New trial license could be generated on [my atlassian](https://my.atlassian.com/license/evaluation).
   Use `BX02-9YO1-IN86-LO5G` Server ID for generation.
   {{% /note %}}

5. Optional variables to override:
   - `jira_version_tag` - Jira Service Management version to deploy. Supported versions see in [README.md](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/README.md). 
   - Make sure that the Jira Service Management version specified in **jira_version_tag** is consistent with the EBS and RDS snapshot versions. Additionally, ensure that corresponding version snapshot lines are uncommented.
6. From local terminal (Git bash terminal for Windows) start the installation (~20 min):
   ``` bash
   docker run --pull=always --env-file aws_envs \
   -v "$PWD/dcapt-small.tfvars:/data-center-terraform/config.tfvars" \
   -v "$PWD/.terraform:/data-center-terraform/.terraform" \
   -v "$PWD/logs:/data-center-terraform/logs" \
   -it atlassianlabs/terraform ./install.sh -c config.tfvars
   ```
7. Copy product URL from the console output. Product url should look like `http://a1234-54321.us-east-2.elb.amazonaws.com/jira`.

{{% note %}}
All the datasets use the standard `admin`/`admin` credentials.
{{% /note %}}

---

### <a id="devtestscenario"></a>2. Run toolkit on the development environment locally

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
    - `application_postfix`: /jira    # default value for TerraForm deployment; e.g., /jira for url like this http://localhost:2990/jira.
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

### <a id="devappaction"></a>3. Develop and test app-specific action locally
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

{{% warning %}}
It is recommended to terminate a development environment before creating an enterprise-scale environment.
Follow [Terminate development environment](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/k8s/README.MD#terminate-development-environment) instructions.
{{% /warning %}}

After adding your custom app-specific actions, you should now be ready to run the required tests for the Marketplace Data Center Apps Approval process. To do this, you'll need an **enterprise-scale environment**.

### <a id="instancesetup"></a>4. Setting up Jira Service Management Data Center enterprise-scale environment with "large" dataset

#### EC2 CPU Limit
The installation of 4-nodes Jira Service Management requires **32** CPU Cores. Make sure that the current EC2 CPU limit is set to higher number of CPU Cores. [AWS Service Quotas](https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas/L-34B43A08) service shows the limit for All Standard Spot Instance Requests. **Applied quota value** is the current CPU limit in the specific region.

The limit can be increased by creating AWS Support ticket. To request the limit increase fill in [Amazon EC2 Limit increase request form](https://aws.amazon.com/contact-us/ec2-request/):

| Parameter             | Value                                                                           |
|-----------------------|---------------------------------------------------------------------------------|
| Limit type            | EC2 Instances                                                                   |
| Severity              | Urgent business impacting question                                              |
| Region                | US East (Ohio) _or your specific region the product is going to be deployed in_ |
| Primary Instance Type | All Standard (A, C, D, H, I, M, R, T, Z) instances                              |
| Limit                 | Instance Limit                                                                  |
| New limit value       | _The needed limit of CPU Cores_                                                 |
| Case description      | _Give a small description of your case_                                         |
Select the **Contact Option** and click **Submit** button.

#### AWS cost estimation
[AWS Pricing Calculator](https://calculator.aws/) provides an estimate of usage charges for AWS services based on certain information you provide.
Monthly charges will be based on your actual usage of AWS services and may vary from the estimates the Calculator has provided.

*The prices below are approximate and may vary depending on such factors like region, instance type, deployment type of DB, and other.  

| Stack | Estimated hourly cost ($) |
| ----- | ------------------------- |
| One Node Jira Service Management DC | 0.8 - 1.1
| Two Nodes Jira Service Management DC | 1.2 - 1.7
| Four Nodes Jira Service Management DC | 2.0 - 3.0

####  Setup Jira Service Management Data Center enterprise-scale environment on k8s

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

Below process describes how to install enterprise-scale Jira Service Management DC with "large" dataset included: 

1. Create [access keys for IAM user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey).
   {{% warning %}}
   Do not use `root` user credentials for cluster creation. Instead, [create an admin user](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-set-up.html#create-an-admin).
   {{% /warning %}}
2. Navigate to `dc-app-perfrormance-toolkit/app/util/k8s` folder.
3. Set AWS access keys created in step1 in `aws_envs` file:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
4. Set **required** variables in `dcapt.tfvars` file:
   - `environment_name` - any name for you environment, e.g. `dcapt-jsm-large`.
   - `products` - `jira`
   - `jira_image_repository` - `atlassian/jira-servicemanagement` - make sure to select the **Jira Service Management** application.
   - `jira_license` - one-liner of valid Jira Service Management license without spaces and new line symbols.
   - `region` - AWS region for deployment.  **Do not change default region (`us-east-2`). If specific region is required, contact support.**
   
   {{% note %}}
   New trial license could be generated on [my atlassian](https://my.atlassian.com/license/evaluation).
   Use `BX02-9YO1-IN86-LO5G` Server ID for generation.
   {{% /note %}}

5. Optional variables to override:
   - `jira_version_tag` - Jira Service Management version to deploy. Supported versions see in [README.md](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/README.md). 
   - Make sure that the Jira Service Management version specified in **jira_version_tag** is consistent with the EBS and RDS snapshot versions. Additionally, ensure that corresponding version snapshot lines are uncommented.
6. From local terminal (Git bash terminal for Windows) start the installation (~40min):
   ``` bash
   docker run --pull=always --env-file aws_envs \
   -v "$PWD/dcapt.tfvars:/data-center-terraform/config.tfvars" \
   -v "$PWD/.terraform:/data-center-terraform/.terraform" \
   -v "$PWD/logs:/data-center-terraform/logs" \
   -it atlassianlabs/terraform ./install.sh -c config.tfvars
   ```
7. Copy product URL from the console output. Product url should look like `http://a1234-54321.us-east-2.elb.amazonaws.com/jira`.

{{% note %}}
All the datasets use the standard `admin`/`admin` credentials.
It's recommended to change default password from UI account page for security reasons.
{{% /note %}}

---

### <a id="executionhost"></a>5. Setting up an execution environment

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
       secure: True                              # Set False to allow insecure connections, e.g. when using self-signed SSL certificate
       application_postfix: /jira                # e.g. /jira for TerraForm deployment url like `http://a1234-54321.us-east-2.elb.amazonaws.com/jira`. Leave this value blank for url without postfix.
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

### <a id="testscenario"></a>6. Running the test scenarios from execution environment against enterprise-scale Jira Service Management Data Center

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
The re-index time for JSM 4.20.x is about ~30-50 minutes, while for JSM 5.4.x it can take significantly longer at around 110-130 minutes. This increase in re-index time is due to a known issue which affects JSM 5.4.x, and you can find more information about it in this ticket: [Re-Index: JSM 9.4.x](https://jira.atlassian.com/browse/JRASERVER-74787).
{{% /note %}}


**Benchmark your re-index time with your app installed:**

1. Install the app you want to test.
2. Setup app license.
3. Go to **![cog icon](/platform/marketplace/images/cog.png) &gt; System &gt; Indexing**.
4. Select the **Full re-index** option.
5. Click **Re-Index** and wait until re-indexing is completed.
{{% note %}}
Jira Service Management will be temporarily unavailable during the re-indexing process. Once the process is complete, the system will be fully accessible and operational once again.
{{% /note %}}

6. **Take a screenshot of the acknowledgment screen** displaying the re-index time and Lucene index timing.
{{% note %}}
Re-index information window is displayed on the **Indexing page**. If the window is not displayed, log in to Jira Service Management one more time and navigate to **![cog icon](/platform/marketplace/images/cog.png) &gt; System &gt; Indexing**. If you use the direct link to the **Indexing** page, refresh the page after the re-index is finished.
{{% /note %}}

7. Attach the screenshot(s) to your ECOHELP ticket.


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
Use [AWS Service Quotas service](https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas/L-34B43A08) to see current limit.
[EC2 CPU Limit](https://developer.atlassian.com/platform/marketplace/dc-apps-performance-toolkit-user-guide-jsm/#ec2-cpu-limit) section has instructions on how to increase limit if needed.
{{% /note %}}

To receive scalability benchmark results for two-node Jira Service Management DC **with** app-specific actions:

1. Navigate to `dc-app-perfrormance-toolkit/app/util/k8s` folder.
2. Open `dcapt.tfvars` file and set `jira_replica_count` value to `2`.
3. From local terminal (Git bash terminal for Windows) start scaling (~20 min):
   ``` bash
   docker run --pull=always --env-file aws_envs \
   -v "$PWD/dcapt.tfvars:/data-center-terraform/config.tfvars" \
   -v "$PWD/.terraform:/data-center-terraform/.terraform" \
   -v "$PWD/logs:/data-center-terraform/logs" \
   -it atlassianlabs/terraform ./install.sh -c config.tfvars
   ```
4. Use SSH to connect to execution environment.
5. Run toolkit with docker from the execution environment instance:

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
Use [AWS Service Quotas service](https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas/L-34B43A08) to see current limit.
[EC2 CPU Limit](https://developer.atlassian.com/platform/marketplace/dc-apps-performance-toolkit-user-guide-jsm/#ec2-cpu-limit) section has instructions on how to increase limit if needed.
{{% /note %}}

To receive scalability benchmark results for four-node Jira Service Management DC with app-specific actions:

1. Scale your Jira Data Center deployment to 4 nodes as described in [Run 4](#run4).
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
It is recommended to terminate an enterprise-scale environment after completing all tests.
Follow [Terminate development environment](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/k8s/README.MD#terminate-enterprise-scale-environment) instructions.
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
For Terraform deploy related questions see  [Troubleshooting tips](https://atlassian-labs.github.io/data-center-terraform/troubleshooting/TROUBLESHOOTING/)page.

If the installation script fails on installing Helm release or any other reason, collect the logs, zip and share to [community Slack](http://bit.ly/dcapt_slack) **#data-center-app-performance-toolkit** channel.
For instructions on how to collect detailed logs, see [Collect detailed k8s logs](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/k8s/README.MD#collect-detailed-k8s-logs).

In case of the above problem or any other technical questions, issues with DC Apps Performance Toolkit, contact us for support in the [community Slack](http://bit.ly/dcapt_slack) **#data-center-app-performance-toolkit** channel.
