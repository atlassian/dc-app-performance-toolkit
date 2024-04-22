---
title: "Data Center App Performance Toolkit User Guide For Crowd"
platform: platform
product: marketplace
category: devguide
subcategory: build
date: "2024-03-19"
---
# Data Center App Performance Toolkit User Guide For Crowd

This document walks you through the process of testing your app on Crowd using the Data Center App Performance Toolkit. These instructions focus on producing the required [performance and scale benchmarks for your Data Center app](/platform/marketplace/dc-apps-performance-and-scale-testing/).

In this document, we cover the use of the Data Center App Performance Toolkit on Enterprise-scale environment.

**Enterprise-scale environment**: Crowd Data Center environment used to generate Data Center App Performance Toolkit test results for the Marketplace approval process. Preferably, use the [AWS Quick Start for Crowd Data Center](https://aws.amazon.com/quickstart/architecture/atlassian-crowd) with the parameters prescribed below. These parameters provision larger, more powerful infrastructure for your Crowd Data Center.

1. [Set up an enterprise-scale environment Crowd Data Center on AWS](#instancesetup).
2. [App-specific actions development](#appspecificaction).
3. [Setting up load configuration for Enterprise-scale runs](#loadconfiguration).
4. [Running the test scenarios from execution environment against enterprise-scale Crowd Data Center](#testscenario).

---

## <a id="instancesetup"></a>1. Set up an enterprise-scale environment Crowd Data Center on k8s

#### EC2 CPU Limit
{{% warning %}}
The installation of 4-pods DC environment and execution pod requires at least **24** vCPU Cores.
Newly created AWS account often has vCPU limit set to low numbers like 5 vCPU per region.
Check your account current vCPU limit for On-Demand Standard instances by visiting [AWS Service Quotas](https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas/L-1216C47A) page.
**Applied quota value** is the current CPU limit in the specific region.

Make that current limit is large enough to deploy new cluster.
The limit can be increased by using **Request increase at account-level** button: choose a region, set a quota value which equals a required number of CPU Cores for the installation and press **Request** button.
Recommended limit is 30.
{{% /warning %}}
#### Setup Crowd Data Center with an enterprise-scale dataset on k8s

Below process describes how to install Crowd DC with an enterprise-scale dataset included. This configuration was created
specifically for performance testing during the DC app review process.

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
   - `environment_name` - any name for you environment, e.g. `dcapt-crowd`
   - `products` - `crowd`
   - `crowd_license` - one-liner of valid crowd license without spaces and new line symbols
   - `region` - **Do not change default region (`us-east-2`). If specific region is required, contact support.**

   {{% note %}}
   New trial license could be generated on [my atlassian](https://my.atlassian.com/license/evaluation).
   Use `BX02-9YO1-IN86-LO5G` Server ID for generation.
   {{% /note %}}

6. From local terminal (Git Bash for Windows users) start the installation (~40min):
   ``` bash
   docker run --pull=always --env-file aws_envs \
   -v "/$PWD/dcapt.tfvars:/data-center-terraform/conf.tfvars" \
   -v "/$PWD/dcapt-snapshots.json:/data-center-terraform/dcapt-snapshots.json" \
   -v "/$PWD/logs:/data-center-terraform/logs" \
   -it atlassianlabs/terraform:2.7.7 ./install.sh -c conf.tfvars
   ```
7. Copy product URL from the console output. Product url should look like `http://a1234-54321.us-east-2.elb.amazonaws.com/crowd`.

---

Data dimensions and values for an enterprise-scale dataset are listed and described in the following table.

| Data dimensions | Value for an enterprise-scale dataset |
| --------------- | ------------------------------------- |
| Users | ~100 000 |
| Groups | ~15 |

{{% note %}}
All the datasets use the standard `admin`/`admin` credentials.
{{% /note %}}
---

{{% note %}}
You are responsible for the cost of the AWS services running during the reference deployment. For more information, 
go to [aws.amazon.com/pricing](https://aws.amazon.com/ec2/pricing/).
{{% /note %}}

To reduce costs, we recommend you to keep your deployment up and running only during the performance runs.

---

## <a id="appspecificaction"></a>2. App-specific actions development

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

## <a id="loadconfiguration"></a>3. Setting up load configuration for Enterprise-scale runs

Default TerraForm deployment [configuration](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/k8s/dcapt.tfvars)
already has a dedicated execution environment pod to run tests from. For more details see `Execution Environment Settings` section in `dcapt.tfvars` file.

1. Check the `crowd.yml` configuration file. If load configuration settings were changed for dev runs, make sure parameters
   were changed back to the defaults:

   ``` yaml
    application_hostname: test_crowd_instance.atlassian.com    # Crowd DC hostname without protocol and port e.g. test-crowd.atlassian.com or localhost
    application_protocol: http      # http or https
    application_port: 80            # 80, 443, 8080, 4990, etc
    secure: True                    # Set False to allow insecure connections, e.g. when using self-signed SSL certificate
    application_postfix: /crowd     # Default postfix value for TerraForm deployment url like `http://a1234-54321.us-east-2.elb.amazonaws.com/crowd`
    admin_login: admin
    admin_password: admin
    application_name: crowd
    application_password: 1111
    load_executor: jmeter            
    concurrency: 1000               # number of concurrent threads to authenticate random users
    test_duration: 45m
   ```  

You'll need to run the toolkit for each [test scenario](#testscenario) in the next section.

---

## <a id="testscenario"></a>4. Running the test scenarios from execution environment against enterprise-scale Crowd Data Center

Using the Data Center App Performance Toolkit for [Performance and scale testing your Data Center app](/platform/marketplace/developing-apps-for-atlassian-data-center-products/) involves two test scenarios:

- [Performance regression](#testscenario1)
- [Scalability testing](#testscenario2)

Each scenario will involve multiple test runs. The following subsections explain both in greater detail.

#### <a id="testscenario1"></a> Scenario 1: Performance regression

This scenario helps to identify basic performance issues without a need to spin up a multi-node Crowd DC. Make sure the app does not have any performance impact when it is not exercised.

##### <a id="regressionrun1"></a> Run 1 (~50 min)

To receive performance baseline results **without** an app installed and **without** app-specific actions (use code from `master` branch):

1. Before run:
   * Make sure `crowd.yml` and toolkit code base has default configuration from the `master` branch. No app-specific actions code applied.
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
    -it atlassianlabs/terraform:2.7.7 bash bzt_on_pod.sh crowd.yml
    ```
1. View the following main results of the run in the `dc-app-performance-toolkit/app/results/crowd/YY-MM-DD-hh-mm-ss` folder:
    - `results_summary.log`: detailed run summary
    - `results.csv`: aggregated .csv file with all actions and timings
    - `bzt.log`: logs of the Taurus tool execution
    - `jmeter.*`: logs of the JMeter tool execution

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps. For an enterprise-scale environment run, the acceptable success rate for actions is 95% and above.
{{% /note %}}

##### <a id="regressionrun2"></a> Run 2 (~50 min)

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
    -it atlassianlabs/terraform:2.7.7 bash bzt_on_pod.sh crowd.yml
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

#### <a id="testscenario2"></a> Scenario 2: Scalability testing

The purpose of scalability testing is to reflect the impact on the customer experience when operating across multiple nodes. 
For this, you have to run scale testing on your app.

For many apps and extensions to Atlassian products, 
there should not be a significant performance difference between operating on a single node or across many nodes in
Crowd DC deployment. To demonstrate performance impacts of operating your app at scale, we recommend testing your Crowd DC app in a cluster.


###### <a id="run3"></a> Run 3 (~50 min)

To receive scalability benchmark results for one-node Crowd DC **with** app-specific actions:

1. Before run:
   * Make sure `crowd.yml` and toolkit code base has code base with your developed app-specific actions.
   * Check correctness of `application_hostname`, `application_protocol`, `application_port` and `application_postfix` in .yml file.
   * Check load configuration parameters needed for enterprise-scale run: [Setting up load configuration for Enterprise-scale runs](#loadconfiguration).
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
    -it atlassianlabs/terraform:2.7.7 bash bzt_on_pod.sh crowd.yml
    ```

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps. For an enterprise-scale environment run, the acceptable success rate for actions is 95% and above.
{{% /note %}}

##### <a id="run4"></a> Run 4 (~50 min)
{{% note %}}
Before scaling your DC make sure that AWS vCPU limit is not lower than needed number. Minimum recommended value is 30.
Use [AWS Service Quotas service](https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas/L-1216C47A) to see current limit.
[EC2 CPU Limit](https://developer.atlassian.com/platform/marketplace/dc-apps-performance-toolkit-user-guide-jira/#ec2-cpu-limit) section has instructions on how to increase limit if needed.
{{% /note %}}

To receive scalability benchmark results for two-node Crowd DC **with** app-specific actions:

1. Navigate to `dc-app-performance-toolkit/app/util/k8s` folder.
1. Open `dcapt.tfvars` file and set `crowd_replica_count` value to `2`.
1. From local terminal (Git Bash for Windows users) start scaling (~20 min):
   ``` bash
   docker run --pull=always --env-file aws_envs \
   -v "/$PWD/dcapt.tfvars:/data-center-terraform/conf.tfvars" \
   -v "/$PWD/dcapt-snapshots.json:/data-center-terraform/dcapt-snapshots.json" \
   -v "/$PWD/logs:/data-center-terraform/logs" \
   -it atlassianlabs/terraform:2.7.7 ./install.sh -c conf.tfvars
   ```
1. Edit **run parameters** for 2 nodes run. To do it, left uncommented only 2 nodes scenario parameters in `crowd.yml` file.
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
    -it atlassianlabs/terraform:2.7.7 bash bzt_on_pod.sh crowd.yml
    ```

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps. For an enterprise-scale environment run, the acceptable success rate for actions is 95% and above.
{{% /note %}}


##### <a id="run5"></a> Run 5 (~50 min)
{{% note %}}
Before scaling your DC make sure that AWS vCPU limit is not lower than needed number. Minimum recommended value is 30.
Use [AWS Service Quotas service](https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas/L-1216C47A) to see current limit.
[EC2 CPU Limit](https://developer.atlassian.com/platform/marketplace/dc-apps-performance-toolkit-user-guide-jira/#ec2-cpu-limit) section has instructions on how to increase limit if needed.
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
    -it atlassianlabs/terraform:2.7.7 bash bzt_on_pod.sh crowd.yml
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
