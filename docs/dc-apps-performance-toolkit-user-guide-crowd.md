---
title: "Data Center App Performance Toolkit User Guide For Crowd"
platform: platform
product: marketplace
category: devguide
subcategory: build
date: "2023-04-20"
---
# Data Center App Performance Toolkit User Guide For Crowd

This document walks you through the process of testing your app on Crowd using the Data Center App Performance Toolkit. These instructions focus on producing the required [performance and scale benchmarks for your Data Center app](/platform/marketplace/dc-apps-performance-and-scale-testing/).

In this document, we cover the use of the Data Center App Performance Toolkit on Enterprise-scale environment.

**Enterprise-scale environment**: Crowd Data Center environment used to generate Data Center App Performance Toolkit test results for the Marketplace approval process. Preferably, use the [AWS Quick Start for Crowd Data Center](https://aws.amazon.com/quickstart/architecture/atlassian-crowd) with the parameters prescribed below. These parameters provision larger, more powerful infrastructure for your Crowd Data Center.

1. [Set up an enterprise-scale environment Crowd Data Center on AWS](#instancesetup).
2. [App-specific actions development](#appspecificaction).   
3. [Set up an execution environment for the toolkit](#executionhost).
4. [Running the test scenarios from execution environment against enterprise-scale Crowd Data Center](#testscenario).

---

## <a id="instancesetup"></a>1. Set up an enterprise-scale environment Crowd Data Center on k8s

We recommend that you use the [official documentation](https://atlassian-labs.github.io/data-center-terraform/) 
how to deploy a Crowd Data Center environment and AWS on k8s. 

#### Setup Crowd Data Center with an enterprise-scale dataset on k8s

Below process describes how to install Crowd DC with an enterprise-scale dataset included. This configuration was created
specifically for performance testing during the DC app review process.

1. Read [requirements](https://atlassian-labs.github.io/data-center-terraform/userguide/PREREQUISITES/#requirements)
   section of the official documentation.
2. Set up [environment](https://atlassian-labs.github.io/data-center-terraform/userguide/PREREQUISITES/#environment-setup).
3. Set up [AWS security credentials](https://atlassian-labs.github.io/data-center-terraform/userguide/INSTALLATION/#1-set-up-aws-security-credentials).
   {{% warning %}}
   Do not use `root` user credentials for cluster creation. Instead, [create an admin user](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-set-up.html#create-an-admin).
   {{% /warning %}}
4. Clone the project repo:
   ```bash
   git clone -b 2.4.0 https://github.com/atlassian-labs/data-center-terraform.git && cd data-center-terraform
   ```
5. Copy [`dcapt.tfvars`](https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/k8s/dcapt.tfvars) file to the `data-center-terraform` folder.
      ``` bash
   wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/k8s/dcapt.tfvars
    ```
6. Set **required** variables in `dcapt.tfvars` file:
   - `environment_name` - any name for you environment, e.g. `dcapt-crowd`
   - `products` - `crowd`
   - `crowd_license` - one-liner of valid crowd license without spaces and new line symbols
   - `region` - **Do not change default region (`us-east-2`). If specific region is required, contact support.**
   - `instance_types` - `["c5.xlarge"]`
7. From local terminal (Git bash terminal for Windows) start the installation (~40min):
   ```bash
   ./install.sh -c dcapt.tfvars
   ```
8. Copy product URL from the console output. Product url should look like `http://a1234-54321.us-east-2.elb.amazonaws.com/crowd`.

{{% note %}}
New trial license could be generated on [my atlassian](https://my.atlassian.com/license/evaluation).
Use `BX02-9YO1-IN86-LO5G` Server ID for generation.
{{% /note %}}

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

#### Troubleshooting
See [Troubleshooting tips](https://atlassian-labs.github.io/data-center-terraform/troubleshooting/TROUBLESHOOTING/) page.

#### Terminate Crowd Data Center

Follow steps described on [Uninstallation and cleanup](https://atlassian-labs.github.io/data-center-terraform/userguide/CLEANUP/) page.

---

{{% note %}}
You are responsible for the cost of the AWS services running during the reference deployment. For more information, 
go to [aws.amazon.com/pricing](https://aws.amazon.com/ec2/pricing/).
{{% /note %}}

To reduce costs, we recommend you to keep your deployment up and running only during the performance runs.

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
    application_postfix: /crowd     # Default postfix value for TerraForm deployment url like `http://a1234-54321.us-east-2.elb.amazonaws.com/crowd`
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

1. Navigate to `data-center-terraform` folder.
2. Open `dcapt.tfvars` file and set `crowd_replica_count` value to `2`.
3. From local terminal (Git bash terminal for Windows) start scaling (~20 min):
   ```bash
   ./install.sh -c dcapt.tfvars
   ```
4. Use SSH to connect to execution environment.

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
For Terraform deploy related questions see  [Troubleshooting tips](https://atlassian-labs.github.io/data-center-terraform/troubleshooting/TROUBLESHOOTING/)page.

If the installation script fails on installing Helm release or any other reason, collect the logs, zip and share to [community Slack](http://bit.ly/dcapt_slack) **#data-center-app-performance-toolkit** channel.  
For instructions on how to do this, see [How to troubleshoot a failed Helm release installation?](https://atlassian-labs.github.io/data-center-terraform/troubleshooting/TROUBLESHOOTING/#_1).

In case of the above problem or any other technical questions, issues with DC Apps Performance Toolkit, contact us for support in the [community Slack](http://bit.ly/dcapt_slack) **#data-center-app-performance-toolkit** channel.
