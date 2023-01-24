---
title: "Data Center App Performance Toolkit User Guide For Bitbucket"
platform: platform
product: marketplace
category: devguide
subcategory: build
date: "2023-01-19"
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
5. [Set up an execution environment for the toolkit](#executionhost).
6. [Running the test scenarios from execution environment against enterprise-scale Bitbucket Data Center](#testscenario).

---

## <a id="mainenvironmentdev"></a>Development environment

Running the tests in a development environment helps familiarize you with the toolkit.
It'll also provide you with a lightweight and less expensive environment for developing app-specific actions.
Once you're ready to generate test results for the Marketplace Data Center Apps Approval process,
run the toolkit in an **enterprise-scale environment**.

---

{{% note %}}
In case you are in the middle of Bitbucket DC app performance testing with the CloudFormation deployment option,
the process can be continued after switching to the `7.1.0` DCAPT version.
{{% /note %}}

* Checkout release `7.1.0` of the `dc-app-performance-toolkit` repository:

   ```
   git checkout release-7.1.0
   ```
* Use the docker container with the `7.1.0` release tag to run performance tests from docker:

   ```
   cd dc-app-performance-toolkit
   docker pull atlassian/dcapt:7.1.0
   docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt:7.1.0 bitbucket.yml
   ```
* The corresponding version of the user guide could be found in the `dc-app-performance-toolkit/docs` folder or by this 
[link](https://github.com/atlassian/dc-app-performance-toolkit/blob/release-7.1.0/docs/dc-apps-performance-toolkit-user-guide-bitbucket.md).
* If specific version of the Bitbucket DC is required, please contact support in the [community Slack](http://bit.ly/dcapt_slack).

---

### <a id="devinstancesetup"></a>1. Setting up Bitbucket Data Center development environment

We recommend that you use the [official documentation](https://atlassian-labs.github.io/data-center-terraform/) 
how to deploy a Bitbucket Data Center environment and AWS on k8s.

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

1. Read [requirements](https://atlassian-labs.github.io/data-center-terraform/userguide/PREREQUISITES/#requirements)
   section of the official documentation.
2. Set up [environment](https://atlassian-labs.github.io/data-center-terraform/userguide/PREREQUISITES/#environment-setup).
3. Set up [AWS security credentials](https://atlassian-labs.github.io/data-center-terraform/userguide/INSTALLATION/#1-set-up-aws-security-credentials).
   {{% warning %}}
   Do not use `root` user credentials for cluster creation. Instead, [create an admin user](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-set-up.html#create-an-admin).
   {{% /warning %}}
4. Clone the project repo:
   ```bash
   git clone -b 2.3.0 https://github.com/atlassian-labs/data-center-terraform.git && cd data-center-terraform
   ```
5. Copy [`dcapt-small.tfvars`](https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/k8s/dcapt-small.tfvars) file to the `data-center-terraform` folder.
   ``` bash
   wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/k8s/dcapt-small.tfvars
    ```
6. Set **required** variables in `dcapt-small.tfvars` file:
   - `environment_name` - any name for you environment, e.g. `dcapt-bitbucket-small`
   - `products` - `bitbucket`
   - `bitbucket_license` - one-liner of valid bitbucket license without spaces and new line symbols
   - `region` - AWS region for deployment. **Do not change default region (`us-east-2`). If specific region is required, contact support.**
7. Optional variables to override:
   - `bitbucket_version_tag` - Bitbucket version to deploy. Supported versions see in [README.md](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/README.md).
8. From local terminal (Git bash terminal for Windows) start the installation (~20 min):
   ```bash
   ./install.sh -c dcapt-small.tfvars
   ```
9. Copy product URL from the console output. Product url should look like `http://a1234-54321.us-east-2.elb.amazonaws.com/bitbucket`.

{{% note %}}
New trial license could be generated on [my atlassian](https://my.atlassian.com/license/evaluation).
Use `BX02-9YO1-IN86-LO5G` Server ID for generation.
{{% /note %}}

{{% note %}}
All the datasets use the standard `admin`/`admin` credentials.
{{% /note %}}

---

### <a id="devtestscenario"></a>2. Run toolkit on the development environment locally

{{% warning %}}
Make sure **English** language is selected as a default language on the **![cog icon](/platform/marketplace/images/cog.png) &gt; General configuration &gt; Languages** page. Other languages are **not supported** by the toolkit.
{{% /warning %}}

{{% warning %}}
Make sure **Remote API** is enabled on the **![cog icon](/platform/marketplace/images/cog.png) &gt; General configuration &gt; Further Configuration** page.
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

We recommend that you use the [official documentation](https://atlassian-labs.github.io/data-center-terraform/) 
how to deploy a Bitbucket Data Center environment and AWS on k8s.

### AWS cost estimation ###
[AWS Pricing Calculator](https://calculator.aws/) provides an estimate of usage charges for AWS services based on certain information you provide.
Monthly charges will be based on your actual usage of AWS services, and may vary from the estimates the Calculator has provided.

*The prices below are approximate and may vary depending on factors such as (region, instance type, deployment type of DB, etc.)

| Stack | Estimated hourly cost ($) |
| ----- | ------------------------- |
| One Node Bitbucket DC | 1.4 - 2.0 |
| Two Nodes Bitbucket DC | 1.7 - 2.5 |
| Four Nodes Bitbucket DC | 2.4 - 3.6 |

#### Setup Bitbucket Data Center enterprise-scale environment on k8s.

Data dimensions and values for an enterprise-scale dataset are listed and described in the following table.

| Data dimensions | Value for an enterprise-scale dataset |
| --------------- | ------------------------------------- |
| Projects | ~25 000 |
| Repositories | ~52 000 |
| Users | ~25 000 |
| Pull Requests | ~ 1 000 000 |
| Total files number | ~750 000 |


{{% warning %}}
It is recommended to terminate a development environment before creating an enterprise-scale environment.
Follow [Uninstallation and Cleanup](https://atlassian-labs.github.io/data-center-terraform/userguide/CLEANUP/) instructions.
If you want to keep a development environment up, read [How do I deal with a pre-existing state in multiple environments?](https://atlassian-labs.github.io/data-center-terraform/troubleshooting/TROUBLESHOOTING/#:~:text=How%20do%20I%20deal%20with%20pre%2Dexisting%20state%20in%20multiple%20environment%3F)
{{% /warning %}}

Below process describes how to install enterprise-scale Bitbucket DC with "large" dataset included: 

1. Read [requirements](https://atlassian-labs.github.io/data-center-terraform/userguide/PREREQUISITES/#requirements)
   section of the official documentation.
2. Set up [environment](https://atlassian-labs.github.io/data-center-terraform/userguide/PREREQUISITES/#environment-setup).
3. Set up [AWS security credentials](https://atlassian-labs.github.io/data-center-terraform/userguide/INSTALLATION/#1-set-up-aws-security-credentials).
   {{% warning %}}
   Do not use `root` user credentials for cluster creation. Instead, [create an admin user](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-set-up.html#create-an-admin).
   {{% /warning %}}
4. Clone the project repo:
   ```bash
   git clone -b 2.3.0 https://github.com/atlassian-labs/data-center-terraform.git && cd data-center-terraform
   ```
5. Copy [`dcapt.tfvars`](https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/k8s/dcapt.tfvars) file to the `data-center-terraform` folder.
      ``` bash
   wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/k8s/dcapt.tfvars
    ```
6. Set **required** variables in `dcapt.tfvars` file:
   - `environment_name` - any name for you environment, e.g. `dcapt-bitbucket-large`
   - `products` - `bitbucket`
   - `bitbucket_license` - one-liner of valid bitbucket license without spaces and new line symbols
   - `region` - AWS region for deployment.  **Do not change default region (`us-east-2`). If specific region is required, contact support.**
   - `instance_types` - `["m5.4xlarge"]` 
7. Optional variables to override:
    - `bitbucket_version_tag` - Bitbucket version to deploy. Supported versions see in [README.md](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/README.md).
8. From local terminal (Git bash terminal for Windows) start the installation (~40min):
    ```bash
    ./install.sh -c dcapt.tfvars
    ```
9. Copy product URL from the console output. Product url should look like `http://a1234-54321.us-east-2.elb.amazonaws.com/bitbucket`.

{{% note %}}
New trial license could be generated on [my atlassian](https://my.atlassian.com/license/evaluation).
Use this server id for generation `BX02-9YO1-IN86-LO5G`.
{{% /note %}}

{{% note %}}
All the datasets use the standard `admin`/`admin` credentials.
It's recommended to change default password from UI account page for security reasons.
{{% /note %}}

{{% warning %}}
Terminate cluster when it is not used for performance results generation.
{{% /warning %}}

---

### <a id="executionhost"></a>5. Setting up an execution environment

For generating performance results suitable for Marketplace approval process use dedicated execution environment. This is a separate AWS EC2 instance to run the toolkit from. Running the toolkit from a dedicated instance but not from a local machine eliminates network fluctuations and guarantees stable CPU and memory performance.

1. Go to GitHub and create a fork of [dc-app-performance-toolkit](https://github.com/atlassian/dc-app-performance-toolkit).
1. Clone the fork locally, then edit the `bitbucket.yml` configuration file. Set enterprise-scale Bitbucket Data Center parameters:

{{% warning %}}
Do not push to the fork real `application_hostname`, `admin_login` and `admin_password` values for security reasons.
Instead, set those values directly in `.yml` file on execution environment instance.
{{% /warning %}}

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
At this stage app-specific actions are not needed yet. Use code from `master` branch with your `bitbucket.yml` changes.
{{% /note %}}

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

##### <a id="regressionrun2"></a> Run 2 (~1 hour)

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

To receive scalability benchmark results for two-node Bitbucket DC **with** app-specific actions:

1. Navigate to `data-center-terraform` folder.
2. Open `dcapt.tfvars` file and set `bitbucket_replica_count` value to `2`.
3. From local terminal (Git bash terminal for Windows) start scaling (~20 min):
   ```bash
   ./install.sh -c dcapt.tfvars
   ```
4. Use SSH to connect to execution environment.
5. Run toolkit with docker from the execution environment instance:
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

1. Scale your Bitbucket Data Center deployment to 4 nodes as described in [Run 4](#run4).
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
1. Once completed, in the `./reports` folder, you will be able to review action timings on Bitbucket Data Center with different numbers of nodes. If you see a significant variation in any action timings between configurations, we recommend taking a look into the app implementation to understand the root cause of this delta.

{{% warning %}}
It is recommended to terminate an enterprise-scale environment after completing all tests.
Follow [Uninstallation and Cleanup](https://atlassian-labs.github.io/data-center-terraform/userguide/CLEANUP/) instructions.
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
See [Troubleshooting tips](https://atlassian-labs.github.io/data-center-terraform/troubleshooting/TROUBLESHOOTING/) page
for Terraform related questions.
In case of technical questions, issues or problems with DC Apps Performance Toolkit, contact us for support in the [community Slack](http://bit.ly/dcapt_slack) **#data-center-app-performance-toolkit** channel.
