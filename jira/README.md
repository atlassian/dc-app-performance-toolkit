# Running Tests
## Pre-requisite
* Working Jira environment. The Performance Toolkit officially supports:
    * The latest Jira GA (General Availability release) - version 8.0.3
    * The latest ER (Enterprise release) - version 7.13.x - coming soon


* Jira application with some users, issues, projects and boards data.
* Client machine with 4 CPUs and 16 GBs of RAM to run the Toolkit.
* Virtual environment with Python3.6+ and bzt installed. See `README.md` for more details.

## Step 0: Prepare jira environment
If you need performance testing results at a production level, follow instructions described 
in official User Guide to set up Jira DC with the corresponding dataset.

For spiking, testing, or developing, your local Jira instance would work well.


## Step 1: Update jira.yml
* `application_hostname`: test jira hostname (without http)
* `application_protocol`: http or https
* `application_port`: 80 (for http) or 443 (for https) or custom
* `application_postfix`: e.g. /jira in case of url like http://localhost:2990/jira
* `admin_login`: jira admin user name (default after dataset upload is admin)
* `admin_password`: jira admin user password (default after dataset upload is admin) 
* `concurrency`: number of concurrent users for JMeter scenario
* `test_duration`: duration of test execution. Default is 1h.
* `WEBDRIVER_VISIBLE`: Visibility of Chrome browser during selenium execution. Default is False.

## Step 2: Run tests
Run Taurus!
```
bzt jira.yml
```

## Results
Results could be found in `resutls/yyyy-mm-dd` directory:
* `bzt.log` - log of bzt run
* `error_artifacts` - folder with screen shots and html's of selenium fails
* `jmeter.err` - JMeter errors log
* `kpi.jtl` - JMeter raw data
* `pytest.out` - detailed log of selenium execution
* `selenium.jtl` - selenium raw data
* `w3c_timings.txt` - w3c browser timings
* `results.csv` - consolidated results of execution


# Useful information

## Jmeter
### Changing JMeter workload
`jira.yml` has a workload section with  a `perc_action_name` fields. You can change values from 0 to 100 to increase/decrease certain actions. The percentages must add up to 100, if you want to ensure the performance script maintains 
throughput defined in `total_actions_per_hr`. The default load simulates an enterprise scale load of 54500 user 
transactions per hour at 200 concurrency.

To simulate a load of medium-sized customers, `total_actions_per_hr` and `concurrency` can be reduced to 14000 transactions 
and 70 users. This can be further halved for a small customer.

### Opening JMeter scripts
JMeter is written in XML and requires the JMeter GUI to view and make changes. You can launch JMeter GUI by running 
`~/.bzt/jmeter-taurus/<jmeter_version>/bin/jmeter`. Be sure to run this command inside the `jira` 
directory. The main `jmeter/jira.jmx` file contains the relative path to other scripts and will throw errors if run elsewhere. 

### Debugging JMeter scripts
Open JMeter UI from  `jira` directory by running `~/.bzt/jmeter-taurus/<jmeter_version>/bin/jmeter`. 
Right-click on `Test Plan` -> `Add` -> `View Resluts Tree`. 
In `View Resluts Tree` click on `Browse` button and open `error.jtl` from `jira/reports/%Y-%m-%d_%H-%M-%S` folder.

From this view you can click on any failed action and see Request and Response data in appropriate tabs.

In addition, you can run and monitor JMeter test real-time on GUI. Launch the test in GUI by running `bzt jira.yml -gui`, add View Results Tree, and start running test (Cmd +r / Ctrl + r).

### Run one JMeter action
####Option 1: Run one JMeter action via UI
1. Launch JMeter GUI by running `~/.bzt/jmeter-taurus/<jmeter_version>/bin/jmeter`.
2. Add correct jira url in `Global Variables` -> `application.domain`.
3. In `Jira` -> `load profile` set `perc_desired_action` to 100.
4. Run JMeter

####Option 2: Run one JMeter action via bzt
1. In jira.yml set `perc_desired_action` to 100 and all other perc_* to 0.
2. Run `bzt jira.yml`

## Selenium
### Debugging Selenium scripts
Detailed log and stacktrace of Selenium PyTest fails could be found in `results/%Y-%m-%d_%H-%M-%S/pytest.out` file. 

Also, under `results/%Y-%m-%d_%H-%M-%S/error_artifacts` there are screenshots and html of Selenium fails.

### Running Selenium tests with Browser UI
There are two options how to run Selenium tests with Browser UI:
1. In `jira.yml` file set `WEBDRIVER_VISIBLE=True`
2. Set environment variable `export WEBDRIVER_VISIBLE=True`


### Running Selenium tests locally without DC App Performance Toolkit
1. Activate virualenv for DC App Performance Toolkit
2. Navigate to jira folder `cd jira`
3. Set Browser visibility `export WEBDRIVER_VISIBLE=True`
4. Run all Selenium PyTest `pytest selenium_ui/jira-ui.py`
5. In order to run one Selenium PyTest (e.g. `test_1_selenium_view_issue`) need to execute first login test and required one:

`pytest selenium_ui/jira-ui.py::test_0_selenium_a_login selenium_ui/jira-ui.py::test_1_selenium_view_issue`


### Comparing different runs
Navigate to `util/reports_generation` folder and follow README.md instructions to generate side-by-side comparison charts.