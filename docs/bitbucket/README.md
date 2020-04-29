# User Guide for Bitbucket
https://developer.atlassian.com/platform/marketplace/dc-apps-performance-toolkit-user-guide-bitbucket/

# Running tests
## Pre-requisites
* Working Bitbucket Server of supported version ([toolkit README](../../README.md) for a list of supported Bitbucket versions) with repos,  etc.
* Client machine with 4 CPUs and 16 GBs of RAM to run the Toolkit.
* Virtual environment with Python3.6+ and bzt installed. See the root [toolkit README](../../README.md) file for more details.
* [Git client](https://git-scm.com/downloads)  

If you need performance testing results at a production level, follow instructions described 
in the official User Guide to set up Bitbucket DC with the corresponding dataset.
For spiking, testing, or developing, your local Bitbucket instance would work well.

## Step 1: Update bitbucket.yml
* `application_hostname`: test bitbucket hostname (without http)
* `application_protocol`: http or https
* `application_port`: 80 (for http) or 443 (for https), or custom
* `application_postfix`: it is empty by default; e.g., /bitbucket for url like this http://localhost:7990/bitbucket
* `admin_login`: bitbucket admin user name (after restoring dataset from SQL dump, the admin user name is: admin)
* `admin_password`: bitbucket admin user password (after restoring dataset from SQL dump, the admin user password is: admin) 
* `concurrency`: number of concurrent users for JMeter scenario
* `test_duration`: duration of test execution (50m is by default)
* `WEBDRIVER_VISIBLE`: visibility of Chrome browser during selenium execution (False is by default)

## Step 2: Run tests
Run Taurus.
```
bzt bitbucket.yml
```

## Results
Results are located in the `resutls/bitbucket/YY-MM-DD-hh-mm-ss` directory:
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
### Opening JMeter scripts
JMeter is written in XML and requires the JMeter GUI to view and make changes. You can launch JMeter GUI by running the `~/.bzt/jmeter-taurus/<jmeter_version>/bin/jmeter` command. 
Be sure to run this command inside the `app` directory. The main [bitbucket.jmx](../../app/jmeter/bitbucket.jmx) file contains the relative path to other scripts and will throw errors if run elsewhere. 

### Debugging JMeter scripts
1. Open JMeter GUI from `app` directory by running the `~/.bzt/jmeter-taurus/<jmeter_version>/bin/jmeter` command. 
2. Right-click `Test Plan` > `Add` > `Listener` > `View Results Tree`. 
3. On the `View Results Tree` page, click the `Browse` button and open `error.jtl` from `app/results/bitbucket/YY-MM-DD-hh-mm-ss` folder.

From this view, you can click on any failed action and see the request and response data in appropriate tabs.

In addition, you can run and monitor JMeter test real-time with GUI.
1. Launch the test with GUI by running `bzt bitbucket.yml -gui`.
2. Right-click `Test Plan` > `Add` > `Listener` > `View Results Tree`. 
3. Click the start button to start running the test.

## Selenium
### Debugging Selenium scripts
Detailed log and stacktrace of Selenium PyTest fails are located in the `results/bitbucket/YY-MM-DD-hh-mm-ss/pytest.out` file. 

Also, screenshots and HTMLs of Selenium fails are stared in the `results/bitbucket/YY-MM-DD-hh-mm-ss/error_artifacts` folder. 

### Running Selenium tests with Browser GUI
There are two options of running Selenium tests with browser GUI:
1. In [bitbucket.yml](../../app/bitbucket.yml) file, set the `WEBDRIVER_VISIBLE: True`.
2. Set environment variable with the `export WEBDRIVER_VISIBLE=True` command.


### Running Selenium tests locally without the Performance Toolkit
1. Activate virualenv for the Performance Toolkit.
2. Navigate to the selenium folder using the `cd app/selenium_ui` command. 
3. Set browser visibility using the `export WEBDRIVER_VISIBLE=True` command.
4. Run all Selenium PyTest tests with the `pytest bitbucket-ui.py` command.
5. To run one Selenium PyTest test (e.g., `test_1_selenium_view_dashboard`), execute the first login test and the required one with this command:

`pytest bitbucket-ui.py::test_0_selenium_a_login bitbucket-ui.py::test_1_selenium_view_dashboard`.


### Comparing different runs
Navigate to the `reports_generation` folder and follow README.md instructions to generate side-by-side comparison charts.
