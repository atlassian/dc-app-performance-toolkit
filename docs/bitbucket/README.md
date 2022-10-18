# User Guide for Bitbucket
https://developer.atlassian.com/platform/marketplace/dc-apps-performance-toolkit-user-guide-bitbucket/

# Running tests
## Pre-requisites
* Working Bitbucket Server of supported version ([toolkit README](../../README.md) for a list of supported Bitbucket versions) with repos,  etc.
* Client machine with 4 CPUs and 16 GBs of RAM to run the Toolkit.
* Virtual environment with Python and bzt installed. See the root [toolkit README](../../README.md) file for more details.
* [Git client](https://git-scm.com/downloads)  

If you need performance testing results at a production level, follow instructions described 
in the official User Guide to set up Bitbucket DC with the corresponding dataset.
For spiking, testing, or developing, your local Bitbucket instance would work well.

## Step 1: Update bitbucket.yml
* `application_hostname`: test bitbucket hostname (without http).
* `application_protocol`: http or https.
* `application_port`: 80 (for http) or 443 (for https), 8080, 7990 or your instance-specific port.
* `secure`: True or False. Default value is True. Set False to allow insecure connections, e.g. when using self-signed SSL certificate.
* `application_postfix`: it is empty by default; e.g., /jira for url like this http://localhost:7990/bitbucket.
* `admin_login`: jira admin user name (after restoring dataset from SQL dump, the admin user name is: admin).
* `admin_password`: jira admin user password (after restoring dataset from SQL dump, the admin user password is: admin) .
* `concurrency`: `20` - number of concurrent users for JMeter scenario.
* `test_duration`: `50m` - duration of test execution.
* `ramp-up`: `10m` - amount of time it will take JMeter to add all test users to test execution.
* `total_actions_per_hour`: `32700` - number of total JMeter actions per hour.
* `WEBDRIVER_VISIBLE`: visibility of Chrome browser during selenium execution (False is by default).

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
1. Open JMeter UI as described in [README.md](../../app/util/jmeter/README.md).
1. On the `View Results Tree` controller, click the `Browse` button and open `error.jtl` from `app/results/bitbucket/YY-MM-DD-hh-mm-ss` folder.

From this view, you can click on any failed action and see the request and response data in appropriate tabs.

## Selenium
### Debugging Selenium scripts
Detailed log and stacktrace of Selenium PyTest fails are located in the `results/bitbucket/YY-MM-DD-hh-mm-ss/pytest.out` file. 

Also, screenshots and HTMLs of Selenium fails are stared in the `results/bitbucket/YY-MM-DD-hh-mm-ss/error_artifacts` folder. 

### Running Selenium tests with Browser GUI
In [bitbucket.yml](../../app/bitbucket.yml) file, set the `WEBDRIVER_VISIBLE: True`.


### Running Selenium tests locally without the Performance Toolkit
1. Activate virualenv for the Performance Toolkit.
1. Navigate to the selenium folder using the `cd app/selenium_ui` command. 
1. In [bitbucket.yml](../../app/bitbucket.yml) file, set the `WEBDRIVER_VISIBLE: True`.
1. Run all Selenium PyTest tests with the `pytest bitbucket_ui.py` command.
1. To run one Selenium PyTest test (e.g., `test_1_selenium_view_dashboard`), execute the first login test and the required one with this command:

`pytest bitbucket_ui.py::test_0_selenium_a_login bitbucket_ui.py::test_1_selenium_view_dashboard`.


### Comparing different runs
Navigate to the `reports_generation` folder and follow README.md instructions to generate side-by-side comparison charts.

### Run prepare data script locally
1. Activate virualenv for the Performance Toolkit.
2. Navigate to the `app` folder.
3. Set PYTHONPATH as full path to `app` folder with command:
    ```bash
    export PYTHONPATH=`pwd`    # for mac or linux
    set PYTHONPATH=%cd%        # for windows
    ```
   
4. Run prepare data script:
    ```bash
    python util/data_preparation/bitbucket_prepare_data.py
    ```
