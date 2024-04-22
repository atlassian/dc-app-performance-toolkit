---
title: "Data Center App Performance Toolkit User Guide For Bitbucket"
platform: platform
product: marketplace
category: devguide
subcategory: build
date: "2024-03-19"
---
# Data Center App Performance Toolkit User Guide For Bitbucket

This document walks you through the process of testing your app on Bitbucket using the Data Center App Performance Toolkit. These instructions focus on producing the required [performance and scale benchmarks for your Data Center app](/platform/marketplace/dc-apps-performance-and-scale-testing/).

In this document, we cover the use of the Data Center App Performance Toolkit on two types of environments:

**[Development environment](#mainenvironmentdev)**: Bitbucket Data Center environment for a test run of Data Center App Performance Toolkit and development of [app-specific actions](#appspecificactions).

1. [Set up a development environment Bitbucket Data Center on AWS](#devinstancesetup).
2. [Run toolkit on the development environment locally](#devtestscenario).
3. [Develop and test app-specific actions locally](#devappaction).

**[Enterprise-scale environment](#mainenvironmententerprise)**: Bitbucket Data Center environment used to generate Data Center App Performance Toolkit test results for the Marketplace approval process.

4. [Set up an enterprise-scale environment Bitbucket Data Center on AWS](#instancesetup).
5. [Setting up load configuration for Enterprise-scale runs](#loadconfiguration).
6. [Running the test scenarios from execution environment against enterprise-scale Bitbucket Data Center](#testscenario).

---

## <a id="mainenvironmentdev"></a>Development environment

Running the tests in a development environment helps familiarize you with the toolkit.
It'll also provide you with a lightweight and less expensive environment for developing app-specific actions.
Once you're ready to generate test results for the Marketplace Data Center Apps Approval process,
run the toolkit in an **enterprise-scale environment**.

### <a id="devinstancesetup"></a>1. Setting up Bitbucket Data Center development environment

#### AWS cost estimation for the development environment

{{% note %}}
You are responsible for the cost of AWS services used while running this Terraform deployment.
See [Amazon EC2 pricing](https://aws.amazon.com/ec2/pricing/) for more detail.
{{% /note %}}

To reduce costs, we recommend you to keep your deployment up and running only during the performance runs.
AWS Bitbucket Data Center development environment infrastructure costs about  20 - 40$ per working week depending on such factors like region, instance type, deployment type of DB, and other.  

#### Setup Bitbucket Data Center development environment on k8s.

{{% note %}}
Bitbucket Data Center development environment is good for app-specific actions development.
But not powerful enough for performance testing at scale.
See [Set up an enterprise-scale environment Bitbucket Data Center on AWS](#instancesetup) for more details.
{{% /note %}}

Below process describes how to install low-tier Bitbucket DC with "small" dataset included:

1. Create [access keys for IAM user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey).
   {{% warning %}}
   Do not use `root` user credentials for cluster creation. Instead, [create an admin user](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-set-up.html#create-an-admin).
   {{% /warning %}}
2. Clone [Data Center App Performance Toolkit](https://github.com/atlassian/dc-app-performance-toolkit) locally.
3. Navigate to `dc-app-performance-toolkit/app/util/k8s` folder.
4. Set AWS access keys created in step1 in `aws_envs` file:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_SESSION_TOKEN` (only for temporary creds)
5. Set **required** variables in `dcapt-small.tfvars` file:
   - `environment_name` - any name for you environment, e.g. `dcapt-bitbucket-small`
   - `products` - `bitbucket`
   - `bitbucket_license` - one-liner of valid bitbucket license without spaces and new line symbols
   - `region` - AWS region for deployment. **Do not change default region (`us-east-2`). If specific region is required, contact support.**

   {{% note %}}
   New trial license could be generated on [my atlassian](https://my.atlassian.com/license/evaluation).
   Use `BX02-9YO1-IN86-LO5G` Server ID for generation.
   {{% /note %}}

6. Optional variables to override:
   - `bitbucket_version_tag` - Bitbucket version to deploy. Supported versions see in [README.md](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/README.md).
7. From local terminal (Git Bash for Windows users) start the installation (~20 min):
   ``` bash
   docker run --env-file aws_envs \
   -v "/$PWD/dcapt-small.tfvars:/data-center-terraform/conf.tfvars" \
   -v "/$PWD/dcapt-snapshots.json:/data-center-terraform/dcapt-snapshots.json" \
   -v "/$PWD/logs:/data-center-terraform/logs" \
   -it atlassianlabs/terraform:2.7.7 ./install.sh -c conf.tfvars
   ```
8. Copy product URL from the console output. Product url should look like `http://a1234-54321.us-east-2.elb.amazonaws.com/bitbucket`.

{{% note %}}
All the datasets use the standard `admin`/`admin` credentials.
{{% /note %}}

---

### <a id="devtestscenario"></a>2. Run toolkit on the development environment locally

{{% warning %}}
Make sure **English** language is selected as a default language on the **![cog icon](/platform/marketplace/images/cog.png) &gt; General configuration &gt; Languages** page. Other languages are **not supported** by the toolkit.
{{% /warning %}}

1. Clone [Data Center App Performance Toolkit](https://github.com/atlassian/dc-app-performance-toolkit) locally.
1. Follow the [README.md](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/README.md) instructions to set up toolkit locally.
1. Navigate to `dc-app-performance-toolkit/app` folder.
1. Open the `bitbucket.yml` file and fill in the following variables:
    - `application_hostname`: your_dc_bitbucket_instance_hostname without protocol.
    - `application_protocol`: http or https.
    - `application_port`: for HTTP - 80, for HTTPS - 443, 8080, 1990 or your instance-specific port.
    - `secure`: True or False. Default value is True. Set False to allow insecure connections, e.g. when using self-signed SSL certificate.
    - `application_postfix`: /bitbucket - default postfix value for TerraForm deployment url like `http://a1234-54321.us-east-2.elb.amazonaws.com/bitbucket`
    - `admin_login`: admin user username.
    - `admin_password`: admin user password.
    - `load_executor`: executor for load tests - [jmeter](https://jmeter.apache.org/)
    - `concurrency`: `1` - number of concurrent JMeter  users.
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

### <a id="devappaction"></a>3. Develop and test app-specific action locally
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
1. If you need to run `app_specific_action` as specific user uncomment `app_specific_user_login` function in [code example](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/extension/bitbucket/extension_ui.py). Note, that in this case `test_1_selenium_custom_action` should follow just before `test_2_selenium_z_log_out` action.
1. In `dc-app-performance-toolkit/app/selenium_ui/bitbucket_ui.py`, review and uncomment the following block of code to make newly created app-specific actions executed:
``` python
# def test_1_selenium_custom_action(webdriver, datasets, screen_shots):
#     app_specific_action(webdriver, datasets)
```

4. Run toolkit with `bzt bitbucket.yml` command to ensure that all Selenium actions including `app_specific_action` are successful.

---
## <a id="mainenvironmententerprise"></a> Enterprise-scale environment

After adding your custom app-specific actions, you should now be ready to run the required tests for the Marketplace Data Center Apps Approval process. To do this, you'll need an **enterprise-scale environment**.

### <a id="instancesetup"></a>4. Setting up Bitbucket Data Center enterprise-scale environment with "large" dataset

{{% warning %}}
It is recommended to terminate a development environment before creating an enterprise-scale environment.
Follow [Terminate development environment](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/k8s/README.MD#terminate-development-environment) instructions.
In case of any problems with uninstall use [Force terminate command](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/k8s/README.MD#force-terminate-cluster).
{{% /warning %}}

#### EC2 CPU Limit
{{% warning %}}
The installation of 4-pods DC environment and execution pod requires at least **40** vCPU Cores.
Newly created AWS account often has vCPU limit set to low numbers like 5 vCPU per region.
Check your account current vCPU limit for On-Demand Standard instances by visiting [AWS Service Quotas](https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas/L-1216C47A) page.
**Applied quota value** is the current CPU limit in the specific region.

Make that current limit is large enough to deploy new cluster.
The limit can be increased by using **Request increase at account-level** button: choose a region, set a quota value which equals a required number of CPU Cores for the installation and press **Request** button.
Recommended limit is 50.
{{% /warning %}}
### AWS cost estimation ###
[AWS Pricing Calculator](https://calculator.aws/) provides an estimate of usage charges for AWS services based on certain information you provide.
Monthly charges will be based on your actual usage of AWS services, and may vary from the estimates the Calculator has provided.

*The prices below are approximate and may vary depending on factors such as (region, instance type, deployment type of DB, etc.)

| Stack                 | Estimated hourly cost ($) |
|-----------------------|---------------------------|
| One pod Bitbucket DC  | 1 - 2
| Two pods Bitbucket DC | 1.5 - 2.5
| Four pods Bitbucket DC   | 2.5 - 4

#### Setup Bitbucket Data Center enterprise-scale environment on k8s.

Data dimensions and values for an enterprise-scale dataset are listed and described in the following table.

| Data dimensions | Value for an enterprise-scale dataset |
| --------------- | ------------------------------------- |
| Projects | ~25 000 |
| Repositories | ~52 000 |
| Users | ~25 000 |
| Pull Requests | ~ 1 000 000 |
| Total files number | ~750 000 |


Below process describes how to install enterprise-scale Bitbucket DC with "large" dataset included: 

1. Create [access keys for IAM user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey).
   {{% warning %}}
   Do not use `root` user credentials for cluster creation. Instead, [create an admin user](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-set-up.html#create-an-admin).
   {{% /warning %}}
2. Clone [Data Center App Performance Toolkit](https://github.com/atlassian/dc-app-performance-toolkit) locally.
3. Navigate to `dc-app-performance-toolkit/app/util/k8s` folder.
4. Set AWS access keys created in step1 in `aws_envs` file:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_SESSION_TOKEN` (only for temporary creds)
5. Set **required** variables in `dcapt.tfvars` file:
   - `environment_name` - any name for you environment, e.g. `dcapt-bitbucket-large`
   - `products` - `bitbucket`
   - `bitbucket_license` - one-liner of valid bitbucket license without spaces and new line symbols
   - `region` - AWS region for deployment.  **Do not change default region (`us-east-2`). If specific region is required, contact support.**

   {{% note %}}
   New trial license could be generated on [my atlassian](https://my.atlassian.com/license/evaluation).
   Use this server id for generation `BX02-9YO1-IN86-LO5G`.
   {{% /note %}}

6. Optional variables to override:
    - `bitbucket_version_tag` - Bitbucket version to deploy. Supported versions see in [README.md](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/README.md).
7. From local terminal (Git Bash for Windows users) start the installation (~40min):
   ``` bash
   docker run --env-file aws_envs \
   -v "/$PWD/dcapt.tfvars:/data-center-terraform/conf.tfvars" \
   -v "/$PWD/dcapt-snapshots.json:/data-center-terraform/dcapt-snapshots.json" \
   -v "/$PWD/logs:/data-center-terraform/logs" \
   -it atlassianlabs/terraform:2.7.7 ./install.sh -c conf.tfvars
   ```
8. Copy product URL from the console output. Product url should look like `http://a1234-54321.us-east-2.elb.amazonaws.com/bitbucket`.

{{% note %}}
All the datasets use the standard `admin`/`admin` credentials.
It's recommended to change default password from UI account page for security reasons.
{{% /note %}}

---

### <a id="loadconfiguration"></a>5. Setting up load configuration for Enterprise-scale runs

Default TerraForm deployment [configuration](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/k8s/dcapt.tfvars)
already has a dedicated execution environment pod to run tests from. For more details see `Execution Environment Settings` section in `dcapt.tfvars` file.

1. Check the `bitbucket.yml` configuration file. If load configuration settings were changed for dev runs, make sure parameters
   were changed back to the defaults:

   ``` yaml
       application_hostname: test_bitbucket_instance.atlassian.com   # Bitbucket DC hostname without protocol and port e.g. test-bitbucket.atlassian.com or localhost
       application_protocol: http        # http or https
       application_port: 80              # 80, 443, 8080, 7990 etc
       secure: True                      # Set False to allow insecure connections, e.g. when using self-signed SSL certificate
       application_postfix:  /bitbucket  # e.g. /bitbucket for TerraForm deployment url like `http://a1234-54321.us-east-2.elb.amazonaws.com/bitbucket`. Leave this value blank for url without postfix.
       admin_login: admin
       admin_password: admin
       load_executor: jmeter             # only jmeter executor is supported
       concurrency: 20                   # number of concurrent virtual users for jmeter scenario
       test_duration: 50m
       ramp-up: 10m                      # time to spin all concurrent users
       total_actions_per_hour: 32700     # number of total JMeter actions per hour
   ```

You'll need to run the toolkit for each [test scenario](#testscenario) in the next section.

---

### <a id="testscenario"></a>6. Running the test scenarios from execution environment against enterprise-scale Bitbucket Data Center

Using the Data Center App Performance Toolkit for [Performance and scale testing your Data Center app](/platform/marketplace/developing-apps-for-atlassian-data-center-products/) involves two test scenarios:

- [Performance regression](#testscenario1)
- [Scalability testing](#testscenario2)

Each scenario will involve multiple test runs. The following subsections explain both in greater detail.

#### <a id="testscenario1"></a> Scenario 1: Performance regression

This scenario helps to identify basic performance issues without a need to spin up a multi-node Bitbucket DC. Make sure the app does not have any performance impact when it is not exercised.

##### <a id="regressionrun1"></a> Run 1 (~1 hour)

To receive performance baseline results **without** an app installed:

1. Before run:
   * Make sure `bitbucket.yml` and toolkit code base has default configuration from the `master` branch.
   * App-specific actions code base is not needed for Run1 and Run2.
   * Check load configuration parameters needed for enterprise-scale run: [Setting up load configuration for Enterprise-scale runs](#loadconfiguration).
   * Check correctness of `application_hostname`, `application_protocol`, `application_port` and `application_postfix` in .yml file.
   * AWS access keys set in `./dc-app-performance-toolkit/app/util/k8s/aws_envs` file:
      - `AWS_ACCESS_KEY_ID`
      - `AWS_SECRET_ACCESS_KEY`
      - `AWS_SESSION_TOKEN` (only for temporary creds)
1. Navigate to `dc-app-performance-toolkit` folder and start tests execution:
    ``` bash
    export ENVIRONMENT_NAME=your_environment_name
    ```

    ``` bash
    docker run --pull=always --env-file ./app/util/k8s/aws_envs \
    -e REGION=us-east-2 \
    -e ENVIRONMENT_NAME=$ENVIRONMENT_NAME \
    -v "/$PWD:/data-center-terraform/dc-app-performance-toolkit" \
    -v "/$PWD/app/util/k8s/bzt_on_pod.sh:/data-center-terraform/bzt_on_pod.sh" \
    -it atlassianlabs/terraform:2.7.7 bash bzt_on_pod.sh bitbucket.yml
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

##### <a id="regressionrun2"></a> Run 2 (~1 hour)

To receive performance results with an app installed (still use master branch):

1. Install the app you want to test.
1. Setup app license.
1. Navigate to `dc-app-performance-toolkit` folder and start tests execution:
    ``` bash
    export ENVIRONMENT_NAME=your_environment_name
    ```

    ``` bash
    docker run --pull=always --env-file ./app/util/k8s/aws_envs \
    -e REGION=us-east-2 \
    -e ENVIRONMENT_NAME=$ENVIRONMENT_NAME \
    -v "/$PWD:/data-center-terraform/dc-app-performance-toolkit" \
    -v "/$PWD/app/util/k8s/bzt_on_pod.sh:/data-center-terraform/bzt_on_pod.sh" \
    -it atlassianlabs/terraform:2.7.7 bash bzt_on_pod.sh bitbucket.yml
    ```

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps. For an enterprise-scale environment run, the acceptable success rate for actions is 95% and above.
{{% /note %}}


##### Generating a performance regression report

To generate a performance regression report:

1. Edit the `./app/reports_generation/performance_profile.yml` file:
   - For `runName: "without app"`, in the `relativePath` key, insert the relative path to results directory of [Run 1](#regressionrun1).
   - For `runName: "with app"`, in the `relativePath` key, insert the relative path to results directory of [Run 2](#regressionrun2).
1. Navigate locally to `dc-app-performance-toolkit` folder and run the following command from local terminal (Git Bash for Windows users) to generate reports:    
    ``` bash
    docker run --pull=always \
    -v "/$PWD:/dc-app-performance-toolkit" \
    --workdir="//dc-app-performance-toolkit/app/reports_generation" \
    --entrypoint="python" \
    -it atlassian/dcapt csv_chart_generator.py performance_profile.yml
    ```
1. In the `./app/results/reports/YY-MM-DD-hh-mm-ss` folder, view the `.csv` file (with consolidated scenario results), the `.png` chart file and performance scenario summary report.
   If you see an impact (>20%) on any action timing, we recommend taking a look into the app implementation to understand the root cause of this delta.

##### <a id="run3"></a> Run 3 (~1 hour)

To receive scalability benchmark results for one-node Bitbucket DC **with** app-specific actions:

1. Before run:
   * Make sure `bitbucket.yml` and toolkit code base has code base with your developed app-specific actions.
   * Check correctness of `application_hostname`, `application_protocol`, `application_port` and `application_postfix` in .yml file.
   * Check load configuration parameters needed for enterprise-scale run: [Setting up load configuration for Enterprise-scale runs](#loadconfiguration).
   * [test_1_selenium_custom_action](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/selenium_ui/bitbucket_ui.py#L67-L68) is uncommented and has implementation in case of Selenium app-specific actions.
   * AWS access keys set in `./dc-app-performance-toolkit/app/util/k8s/aws_envs` file:
      - `AWS_ACCESS_KEY_ID`
      - `AWS_SECRET_ACCESS_KEY`
      - `AWS_SESSION_TOKEN` (only for temporary creds)
1. Navigate to `dc-app-performance-toolkit` folder and start tests execution:
    ``` bash
    export ENVIRONMENT_NAME=your_environment_name
    ```

    ``` bash
    docker run --pull=always --env-file ./app/util/k8s/aws_envs \
    -e REGION=us-east-2 \
    -e ENVIRONMENT_NAME=$ENVIRONMENT_NAME \
    -v "/$PWD:/data-center-terraform/dc-app-performance-toolkit" \
    -v "/$PWD/app/util/k8s/bzt_on_pod.sh:/data-center-terraform/bzt_on_pod.sh" \
    -it atlassianlabs/terraform:2.7.7 bash bzt_on_pod.sh bitbucket.yml
    ```
   
{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps. For an enterprise-scale environment run, the acceptable success rate for actions is 95% and above.
{{% /note %}}


##### <a id="run4"></a> Run 4 (~1 hour)
{{% note %}}
Before scaling your DC make sure that AWS vCPU limit is not lower than needed number. Minimum recommended value is 50.
Use [AWS Service Quotas service](https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas/L-1216C47A) to see current limit.
[EC2 CPU Limit](https://developer.atlassian.com/platform/marketplace/dc-apps-performance-toolkit-user-guide-jira/#ec2-cpu-limit) section has instructions on how to increase limit if needed.
{{% /note %}}

To receive scalability benchmark results for two-node Bitbucket DC **with** app-specific actions:

1. Navigate to `dc-app-performance-toolkit/app/util/k8s` folder.
1. Open `dcapt.tfvars` file and set `bitbucket_replica_count` value to `2`.
1. From local terminal (Git Bash for Windows users) start scaling (~20 min):
   ``` bash
   docker run --pull=always --env-file aws_envs \
   -v "/$PWD/dcapt.tfvars:/data-center-terraform/conf.tfvars" \
   -v "/$PWD/dcapt-snapshots.json:/data-center-terraform/dcapt-snapshots.json" \
   -v "/$PWD/logs:/data-center-terraform/logs" \
   -it atlassianlabs/terraform:2.7.7 ./install.sh -c conf.tfvars
   ```
1. Navigate to `dc-app-performance-toolkit` folder and start tests execution:
    ``` bash
    export ENVIRONMENT_NAME=your_environment_name
    ```

    ``` bash
    docker run --pull=always --env-file ./app/util/k8s/aws_envs \
    -e REGION=us-east-2 \
    -e ENVIRONMENT_NAME=$ENVIRONMENT_NAME \
    -v "/$PWD:/data-center-terraform/dc-app-performance-toolkit" \
    -v "/$PWD/app/util/k8s/bzt_on_pod.sh:/data-center-terraform/bzt_on_pod.sh" \
    -it atlassianlabs/terraform:2.7.7 bash bzt_on_pod.sh bitbucket.yml
    ```

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps. For an enterprise-scale environment run, the acceptable success rate for actions is 95% and above.
{{% /note %}}


##### <a id="run5"></a> Run 5 (~1 hour)
{{% note %}}
Before scaling your DC make sure that AWS vCPU limit is not lower than needed number. Minimum recommended value is 50.
Use [AWS Service Quotas service](https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas/L-1216C47A) to see current limit.
[EC2 CPU Limit](https://developer.atlassian.com/platform/marketplace/dc-apps-performance-toolkit-user-guide-jira/#ec2-cpu-limit) section has instructions on how to increase limit if needed.
{{% /note %}}

To receive scalability benchmark results for four-node Bitbucket DC with app-specific actions:

1. Scale your Bitbucket Data Center deployment to 4 nodes as described in [Run 4](#run4).
1. Navigate to `dc-app-performance-toolkit` folder and start tests execution:
    ``` bash
    export ENVIRONMENT_NAME=your_environment_name
    ```

    ``` bash
    docker run --pull=always --env-file ./app/util/k8s/aws_envs \
    -e REGION=us-east-2 \
    -e ENVIRONMENT_NAME=$ENVIRONMENT_NAME \
    -v "/$PWD:/data-center-terraform/dc-app-performance-toolkit" \
    -v "/$PWD/app/util/k8s/bzt_on_pod.sh:/data-center-terraform/bzt_on_pod.sh" \
    -it atlassianlabs/terraform:2.7.7 bash bzt_on_pod.sh bitbucket.yml
    ```

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps. For an enterprise-scale environment run, the acceptable success rate for actions is 95% and above.
{{% /note %}}


#### Generating a report for scalability scenario

To generate a scalability report:

1. Edit the `./app/reports_generation/scale_profile.yml` file:
   - For `runName: "1 Node"`, in the `relativePath` key, insert the relative path to results directory of [Run 3](#run3).
   - For `runName: "2 Nodes"`, in the `relativePath` key, insert the relative path to results directory of [Run 4](#run4).
   - For `runName: "4 Nodes"`, in the `relativePath` key, insert the relative path to results directory of [Run 5](#run5).
1. Navigate locally to `dc-app-performance-toolkit` folder and run the following command from local terminal (Git Bash for Windows users) to generate reports:   
    ``` bash
    docker run --pull=always \
    -v "/$PWD:/dc-app-performance-toolkit" \
    --workdir="//dc-app-performance-toolkit/app/reports_generation" \
    --entrypoint="python" \
    -it atlassian/dcapt csv_chart_generator.py scale_profile.yml
    ```
1. In the `./app/results/reports/YY-MM-DD-hh-mm-ss` folder, view the `.csv` file (with consolidated scenario results), the `.png` chart file and performance scenario summary report.
   If you see an impact (>20%) on any action timing, we recommend taking a look into the app implementation to understand the root cause of this delta.

{{% warning %}}
It is recommended to terminate an enterprise-scale environment after completing all tests.
Follow [Terminate enterprise-scale environment](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/k8s/README.MD#terminate-enterprise-scale-environment) instructions.
In case of any problems with uninstall use [Force terminate command](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/k8s/README.MD#force-terminate-cluster).
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
If the installation script fails on installing Helm release or any other reason, collect the logs, zip and share to [community Slack](http://bit.ly/dcapt_slack) **#data-center-app-performance-toolkit** channel.
For instructions on how to collect detailed logs, see [Collect detailed k8s logs](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/k8s/README.MD#collect-detailed-k8s-logs).
For failed cluster uninstall use [Force terminate command](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/k8s/README.MD#force-terminate-cluster).

In case of any technical questions or issues with DC Apps Performance Toolkit, contact us for support in the [community Slack](http://bit.ly/dcapt_slack) **#data-center-app-performance-toolkit** channel.
