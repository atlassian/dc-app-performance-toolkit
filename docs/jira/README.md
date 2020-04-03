# User Guide for Jira
https://developer.atlassian.com/platform/marketplace/dc-apps-performance-toolkit-user-guide-jira/

# Running tests
## Pre-requisites
* Working Jira Software of supported version ([toolkit README](../../README.md) for a list of supported Jira versions) with users, issues, projects, and boards, etc.
* Client machine with 4 CPUs and 16 GBs of RAM to run the Toolkit.
* Virtual environment with Python3.6+ and bzt installed. See the root [toolkit README](../../README.md) file for more details.

If you need performance testing results at a production level, follow instructions described 
in the official User Guide to set up Jira DC with the corresponding dataset.
For spiking, testing, or developing, your local Jira instance would work well.

## Step 1: Update jira.yml
* `application_hostname`: test jira hostname (without http)
* `application_protocol`: http or https
* `application_port`: 80 (for http) or 443 (for https), or custom
* `application_postfix`: it is empty by default; e.g., /jira for url like this http://localhost:2990/jira
* `admin_login`: jira admin user name (after restoring dataset from SQL dump, the admin user name is: admin)
* `admin_password`: jira admin user password (after restoring dataset from SQL dump, the admin user password is: admin) 
* `concurrency`: number of concurrent users for JMeter scenario
* `test_duration`: duration of test execution (45m is by default)
* `WEBDRIVER_VISIBLE`: visibility of Chrome browser during selenium execution (False is by default)

## Step 2: Run tests
Run Taurus.
```
bzt jira.yml
```

## Results
Results are located in the `resutls/jira/YY-MM-DD-hh-mm-ss` directory:
* `bzt.log` - log of bzt run
* `error_artifacts` - folder with screenshots and HTMLs of Selenium fails
* `jmeter.err` - JMeter errors log
* `kpi.jtl` - JMeter raw data
* `pytest.out` - detailed log of Selenium execution, including stacktraces of Selenium fails
* `selenium.jtl` - Selenium raw data
* `results.csv` - consolidated results of execution
* `resutls_summary.log` - detailed summary of the run. Make sure that overall run status is `OK` before moving to the 
next steps.


# Useful information

## Jmeter
### Changing JMeter workload
The [jira.yml](../../app/jira.yml) has a workload section with `perc_action_name` fields. You can change values from 0 to 100 to increase/decrease execution frequency of certain actions. 
The percentages must add up to 100, if you want to ensure the performance script maintains 
throughput defined in `total_actions_per_hr`. The default load simulates an enterprise scale load of 54500 user transactions per hour at 200 concurrency.

To simulate a load of medium-sized customers, `total_actions_per_hr` and `concurrency` can be reduced to 14000 transactions and 70 users. This can be further halved for a small customer.

### Opening JMeter scripts
JMeter is written in XML and requires the JMeter GUI to view and make changes. You can launch JMeter GUI by running the `~/.bzt/jmeter-taurus/<jmeter_version>/bin/jmeter` command. 
Be sure to run this command inside the `app` directory. The main [jira.jmx](../../app/jmeter/jira.jmx) file contains the relative path to other scripts and will throw errors if run elsewhere. 

### Debugging JMeter scripts
1. Open JMeter GUI from `jira` directory by running the `~/.bzt/jmeter-taurus/<jmeter_version>/bin/jmeter` command. 
2. Right-click `Test Plan` > `Add` > `Listener` > `View Results Tree`. 
3. On the `View Results Tree` page, click the `Browse` button and open `error.jtl` from `app/results/jira/YY-MM-DD-hh-mm-ss` folder.

From this view, you can click on any failed action and see the request and response data in appropriate tabs.

In addition, you can run and monitor JMeter test real-time with GUI.
1. Launch the test with GUI by running `bzt jira.yml -gui`.
2. Right-click `Test Plan` > `Add` > `Listener` > `View Results Tree`. 
3. Click the start button to start running the test.

### Run one JMeter action
#### Option 1: Run one JMeter action via GUI
1. Open JMeter GUI from `app` directory by running the `~/.bzt/jmeter-taurus/<jmeter_version>/bin/jmeter` command. 
2. Go to `File` > `Open`, and then open `jmeter/jira.jmx`.
2. In the`Global Variables` section, add correct Jira hostname, port, protocol, and postfix (if required).
3. In `Jira` > `load profile`, set `perc_desired_action` to 100.
4. Run JMeter.

#### Option 2: Run one JMeter action via bzt
1. In [jira.yml](../../app/jira.yml), set `perc_desired_action` to 100 and all other perc_* to 0.
2. Run `bzt jira.yml`.

## Selenium
### Debugging Selenium scripts
Detailed log and stacktrace of Selenium PyTest fails are located in the `results/jira/YY-MM-DD-hh-mm-ss/pytest.out` file. 

Also, screenshots and HTMLs of Selenium fails are stared in the `results/jira/YY-MM-DD-hh-mm-ss/error_artifacts` folder. 

### Running Selenium tests with Browser GUI
There are two options of running Selenium tests with browser GUI:
1. In [jira.yml](../../app/jira.yml) file, set the `WEBDRIVER_VISIBLE: True`.
2. Set environment variable with the `export WEBDRIVER_VISIBLE=True` command.


### Running Selenium tests locally without the Performance Toolkit
1. Activate virualenv for the Performance Toolkit.
2. Navigate to the selenium folder using the `cd app/selenium_ui` command. 
3. Set browser visibility using the `export WEBDRIVER_VISIBLE=True` command.
4. Run all Selenium PyTest tests with the `pytest jira-ui.py` command.
5. To run one Selenium PyTest test (e.g., `test_1_selenium_view_issue`), execute the first login test and the required one with this command:

`pytest jira-ui.py::test_0_selenium_a_login jira-ui.py::test_1_selenium_view_issue`.


### Comparing different runs
Navigate to the `reports_generation` folder and follow README.md instructions to generate side-by-side comparison charts.
