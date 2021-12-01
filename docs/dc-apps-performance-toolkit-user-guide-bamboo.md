---
title: "Data Center App Performance Toolkit User Guide For Bamboo"
platform: platform
product: marketplace
category: devguide
subcategory: build
date: "2021-12-10"
---
# Data Center App Performance Toolkit User Guide For Bamboo

This document walks you through the process of testing your app on Bamboo using the Data Center App Performance Toolkit. 
These instructions focus on producing the required 
[performance and scale benchmarks for your Data Center app](https://developer.atlassian.com/platform/marketplace/dc-apps-performance-and-scale-testing/).

In this document, we cover the use of the Data Center App Performance Toolkit on Enterprise-scale environment.

**Enterprise-scale environment**: Bamboo Data Center environment used to generate Data Center App Performance Toolkit 
test results for the Marketplace approval process. Preferably, use the below recommended parameters.

1. [Set up an enterprise-scale environment Bamboo Data Center on AWS](#instancesetup).
2. [Load an enterprise-scale dataset on your Bamboo Data Center deployment](#preloading).
3. [App-specific actions development](#appspecificaction).   
4. [Set up an execution environment for the toolkit](#executionhost).
5. [Running the test scenarios from execution environment against enterprise-scale Bamboo Data Center](#testscenario).

---

## <a id="instancesetup"></a>1. Set up an enterprise-scale environment Bamboo Data Center on AWS

We recommend that you use the 
[official documentation](https://confluence.atlassian.com/bamboo/running-bamboo-data-center-on-a-single-node-1063170549.html) 
how to deploy a Bamboo Data Center environment.

#### Setup Bamboo Data Center

[Bamboo installation guide](https://confluence.atlassian.com/bamboo/bamboo-installation-guide-289276785.html) describes 
installation flow for [linux environment](https://confluence.atlassian.com/bamboo/installing-bamboo-on-linux-289276792.html):
1. [Launch AWS EC2 instance](https://docs.aws.amazon.com/quickstarts/latest/vmlaunch/step-1-launch-instance.html). 
   * OS: select from Quick Start `Ubuntu Server 20.04 LTS`.
   * Instance type: [`m5.xlarge`](https://aws.amazon.com/ec2/instance-types/m5/)
   * Storage size: `100` GiB
  
1. Create DB in AWS:
   1. Go to AWS RDS service.
   1. Click **Create database** button.
   1. Select **Postgre SQL** and version **PostgreSQL 12**.
   1. Input **DB instance identifier**.
   1. Input **Master password** and **Confirm password**.
   1. Select **DB instance class** as **db.t3.medium**. 
   1. In **Storage** section select **Storage type** to **General Purpose SSD** and **Allocated storage** to **100** GiB.
   1. In **Availability & durability** section select **Do not create a standby instance** option.
   1. In **Connectivity** section select the same **Virtual private cloud (VPC)** as your Bamboo instance.
   1. In **Connectivity** section set **Public access** option to **No**.
   1. In **Connectivity** section select **VPC security group** option to **Choose existing** and set to the same as your Bamboo instance.
   1. Set **Database authentication** to **Password authentication**.
   1. Click **Create database** button.
   1. Wait till DB is created and copy DB **Endpoint** from RDS -> Databases -> your DB -> **Connectivity & security** tab.

1. Edit Bamboo instance security group to allow inbound **TCP** traffic on port `8085` from anywhere.

1. Edit Bamboo instance security group to allow inbound **PostgreSQL** traffic on port `5432` from Bamboo instance **Private IP**.

1. Connect to the Bamboo instance using [SSH](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html) 
   or the [AWS Systems Manager Sessions Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html).

   ```bash
   ssh -i path_to_pem_file ubuntu@BAMBOO_INSTANCE_PUBLIC_IP
   ```
   
1. Install jdk:
   
   ```bash
   sudo apt-get update
   sudo apt install -y openjdk-11-jre-headless
   ```

1. Setup `JAVA_HOME` variable:
   
   ```bash
   export JAVA_HOME=$(java -XshowSettings:properties -version 2>&1 > /dev/null | grep 'java.home' | awk {'print $3'})
   echo "export JAVA_HOME=$JAVA_HOME" | sudo tee -a /etc/profile
   echo 'export PATH=$JAVA_HOME/bin:$PATH' | sudo tee -a /etc/profile
   source /etc/profile
   ```
   
1. Setup DB on the instance:

   ```bash
   sudo apt-get update
   sudo apt-get install -y postgresql-client
   export DB_HOST=YOUR_DB_ENDPOINT
   # create bamboouser
   PGPASSWORD=YOUR_DB_MASTERPASSWORD psql -h ${DB_HOST} -U postgres -c "create user bamboouser;"
   # set password for bamboouser
   PGPASSWORD=YOUR_DB_MASTERPASSWORD psql -h ${DB_HOST} -U postgres -c "alter user bamboouser with password 'new_strong_pass';"
   # create db
   PGPASSWORD=YOUR_DB_MASTERPASSWORD psql -h ${DB_HOST} -U postgres -c "create database bamboo;"
   # change owner
   PGPASSWORD=YOUR_DB_MASTERPASSWORD psql -h ${DB_HOST} -U postgres -c "alter database bamboo owner to bamboouser;"
   ```

1. Install Bamboo `8.1.0`:
   Follows [installation instructions](https://confluence.atlassian.com/bamboo/installing-bamboo-on-linux-289276792.html).

1. Go to Bamboo UI in browser `http://BAMBOO_INSTANCE_PUBLIC_IP:8085` and follow setup wizard flow:
   1. On the **License** page enter license by either:
    - Using your existing license, or
    - Generating an evaluation license, or
    - Contacting Atlassian to be provided two time-bomb licenses for testing. Ask for it in your DCHELP ticket.
    Click **Continue**.
   1. On the **Configure instance** page left all the defaults and click **Continue**.
   1. On the **Configure database** page select database type to `PostgresSQL` and click **Continue**.
   1. On the **Configure how Bamboo will connect to your database** page:
    - **Connection type**: Connect using JDBC
    - **Driver class name**: org.postgresql.Driver
    - **Database URL**: jdbc:postgresql://YOUR_DB_ENDPOINT:5432/bamboo
    - **User name**: bamboouser
    - **Password**: PASSWORD_FOR_BAMBOO_USER
   1. On the **Import data** page select **Create a new Bamboo home** page and click **Continue**.
   1. On the **Create admin** page, fill in the following fields:
    - **Username**: admin _(recommended)_
    - **Password**: admin _(recommended)_
    - **Confirm Password**: admin _(recommended)_
    - **Full name**: a full name of the admin user
    - **Email Address**: email address of the admin user
    Then select **Finish**.
      
1. Setup remote agents instance:
   1. [Launch AWS EC2 instance](https://docs.aws.amazon.com/quickstarts/latest/vmlaunch/step-1-launch-instance.html). 
   *  OS: select from Quick Start `Ubuntu Server 20.04 LTS`.
   * Instance type: [`m5.2xlarge`](https://aws.amazon.com/ec2/instance-types/m5/)
   * Storage size: `100` GiB
   * Select the same security group as your Bamboo instance.
   
1. Edit Bamboo instance security group to allow inbound **Custom TCP** traffic on port `54663` from Agents instance **Private IP**.

1. Connect to the Agents instance using [SSH](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html) 
   or the [AWS Systems Manager Sessions Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html).

   ```bash
   ssh -i path_to_pem_file ubuntu@AGENTS_INSTANCE_PUBLIC_IP
   ```
   
1. Setup remote agents:
   - Download `agents_setup.sh` file   

   ```bash
   wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/bamboo/agents_setup.sh && chmod +x agents_setup.sh
   ```
   
   - Edit `agents_setup.sh` file and set correct `BAMBOO_URL`, `USERNAME` and `PASSWORD` values.
   
   - Run command:
   
   ```bash
   ./agents_setup.sh 2>&1 | tee -a agents_setup.log
   ```
   
{{% note %}}
You are responsible for the cost of the AWS services running during the reference deployment. For more information, 
go to [aws.amazon.com/pricing](https://aws.amazon.com/ec2/pricing/).
{{% /note %}}

To reduce costs, we recommend you to keep your deployment up and running only during the performance runs.

#### AWS cost estimation
[AWS Pricing Calculator](https://calculator.aws/) provides an estimate of usage charges for AWS services based on certain information you provide.
Monthly charges will be based on your actual usage of AWS services and may vary from the estimates the Calculator has provided.

*The prices below are approximate and may vary depending on such factors like region, instance type, deployment type of DB, and other.  


| Stack | Estimated hourly cost ($) |
| ----- | ------------------------- |
| One Node Bamboo DC + Agents instance | 0.7 - 0.8

#### Stop Bamboo instance and Agents instance

To reduce AWS infrastructure costs you could stop bamboo node or agents instance in AWS EC2 console:

1. Go to EC2 **Instances**, select instance, click **Instance state** > **Stop instance**.

To return node into a working state follow the instructions:  

1. Go to EC2 **Instances**, select instance, click **Instance state** > **Start instance**, wait a few minutes for node to become available.

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

{{% note %}}
After [Preloading your Bamboo deployment with an enterprise-scale dataset](#preloading), the admin user will have `admin`/`admin` credentials.
{{% /note %}}

---

## <a id="preloading"></a>2. Preloading your Bamboo deployment with an enterprise-scale dataset

Data dimensions and values for an enterprise-scale dataset are listed and described in the following table.

| Data dimensions | Value for an enterprise-scale dataset |
| --------------- | ------------------------------------- |
| Users | 2000 |
| Projects | 100 |
| Plans | 2000 |
| Remote agents | 50 |

{{% note %}}
All the datasets use the standard `admin`/`admin` credentials.
{{% /note %}}

#### Pre-loading the dataset:

[Importing the main dataset](#importingdataset). To help you out, we provide an enterprise-scale dataset you can import.

#### <a id="importingdataset"></a> Importing the main dataset through import (~30 minutes)

1. Connect to the Bamboo instance using [SSH](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html) 
   or the [AWS Systems Manager Sessions Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html).

   ```bash
   ssh -i path_to_pem_file ubuntu@BAMBOO_INSTANCE_PUBLIC_IP
   ```
   
1. Download the dcapt-bamboo.zip file:

    ``` bash
    wget https://centaurus-datasets.s3.amazonaws.com/bamboo/dcapt-bamboo.zip -O /home/ubuntu/bamboo-home/shared/dcapt-bamboo.zip
    ```
   
1. Log in as a user with the **Bamboo System Administrators** [global permission](https://confluence.atlassian.com/adminjiraserver/managing-global-permissions-938847142.html).
1. Go to **![cog icon](/platform/marketplace/images/cog.png) &gt; Overview &gt; Import** from the menu.
1. Populate the **Restore file path** field with `home/ubuntu/bamboo-home/shared/dcapt-bamboo.zip`.
1. Uncheck **Backup data** option.
1. Check **Clear artifact directory** option.
1. Click **Import** and **Confirm** and wait until the import is completed.
1. Restart Bamboo:

    ``` bash
    cd <Bamboo installation directory>
    ./bin/stop-bamboo.sh 
    ./bin/start-bamboo.sh 
    ```
   
---

## <a id="appspecificaction"></a>3. App-specific actions development

Data Center App Performance Toolkit has its own set of default test actions: JMeter for load at scale generation, selenium for UI timings measuring and locust for steady parallel plans running.     

**App-specific action** - action (performance test) you have to develop to cover main use cases of your application. 
Performance test should focus on the common usage of your application and not to cover all possible functionality of 
your app. For example, application setup screen or other one-time use cases are out of scope of performance testing.

**JMeter app-specific actions development**

1. Set up local environment for toolkit using the [README](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/README.md).
1. Check that `bamboo.yml` file has correct settings of `application_hostname`, `application_protocol`, `application_port`, `application_postfix`, etc.
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
1. [Launch AWS EC2 instance](https://docs.aws.amazon.com/quickstarts/latest/vmlaunch/step-1-launch-instance.html). 
   * OS: select from Quick Start `Ubuntu Server 18.04 LTS`.
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
1. On the **Update** tab, select **Use current template**, and then click **Next**.
1. Enter `2` in the **Maximum number of cluster nodes** and the **Minimum number of cluster nodes** fields.
1. Click **Next** > **Next** > **Update stack** and wait until stack is updated.
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
1. Run toolkit with docker from the execution environment instance:

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

#### Attaching testing results to DCHELP ticket

{{% warning %}}
Do not forget to attach performance testing results to your DCHELP ticket.
{{% /warning %}}

1. Make sure you have two reports folders: one with performance profile and second with scale profile results. 
   Each folder should have `profile.csv`, `profile.png`, `profile_summary.log` and profile run result archives.
1. Attach two reports folders to your DCHELP ticket.

## <a id="support"></a> Support
In case of technical questions, issues or problems with DC Apps Performance Toolkit, contact us for support in the [community Slack](http://bit.ly/dcapt_slack) **#data-center-app-performance-toolkit** channel.
