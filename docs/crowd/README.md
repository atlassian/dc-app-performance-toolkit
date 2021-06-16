# User Guide for Crowd
https://developer.atlassian.com/platform/marketplace/dc-apps-performance-toolkit-user-guide-crowd/

# Running tests
## Pre-requisites
* Working Crowd Software of supported version ([toolkit README](../../README.md) for a list of supported Crowd versions) with users, groups, etc.
* Client machine with 4 CPUs and 16 GBs of RAM to run the Toolkit.
* Virtual environment with Python and bzt installed. See the root [toolkit README](../../README.md) file for more details.

If you need performance testing results at a production level, follow instructions described 
in the official User Guide to set up Crowd DC with the corresponding dataset.
For spiking, testing, or developing, your local Crowd instance would work well.

## Step 1: Update crowd.yml
* `application_hostname`: test crowd hostname (without http).
* `application_protocol`: http or https.
* `application_port`: 80 (for http) or 443 (for https), 8080, 4990 or your instance-specific port.
* `secure`: True or False. Default value is True. Set False to allow insecure connections, e.g. when using self-signed SSL certificate.
* `application_postfix`: it is empty by default; e.g., /crowd for url like this http://localhost:4990/crowd.
* `admin_login`: crowd admin username (after restoring dataset from SQL dump, the admin user name is: admin).
* `admin_password`: crowd admin user password (after restoring dataset from SQL dump, the admin user password is: admin) .
* `application_name`: name of crowd application.  
* `application_password`: password of crowd application.
* `load_executor`: `jmeter`.
* `concurrency`: `1000` - number of concurrent users for JMeter scenario.
* `test_duration`: `45m` - duration of test execution.

## Step 2: Run tests
Run Taurus.
```
bzt crowd.yml
```

## Results
Results are located in the `resutls/crowd/YY-MM-DD-hh-mm-ss` directory:
* `bzt.log` - log of bzt run
* `error_artifacts` - folder with screenshots and HTMLs of Selenium fails
* `jmeter.err` - JMeter errors log
* `kpi.jtl` - JMeter raw data
* `results.csv` - consolidated results of execution
* `resutls_summary.log` - detailed summary of the run. Make sure that overall run status is `OK` before moving to the 
next steps.


# Useful information

## Changing performance workload for JMeter
The [crowd.yml](../../app/crowd.yml) has three pairs of parameters for different workload depends on crowd instance nodes count. 
``` 
    # 1 node scenario parameters
    ramp-up: 20s                    # time to spin all concurrent threads
    total_actions_per_hour: 180000  # number of total JMeter actions per hour

    # 2 nodes scenario parameters
    # ramp-up: 10s                    # time to spin all concurrent threads
    # total_actions_per_hour: 360000  # number of total JMeter actions per hour

    # 4 nodes scenario parameters
    # ramp-up: 5s                     # time to spin all concurrent threads
    # total_actions_per_hour: 720000  # number of total JMeter actions per hour
   ```
Uncomment appropriate part of configs to produce necessary instance workload.
For app-specific actions development and testing it's ok to reduce concurrency, test_duration, total_actions_per_hour and ramp-up.

## JMeter
### Debugging JMeter scripts
1. Open JMeter UI as described in [README.md](../../app/util/jmeter/README.md).
1. On the `View Results Tree` controller, click the `Browse` button and open `error.jtl` from `app/results/crowd/YY-MM-DD-hh-mm-ss` folder.

From this view, you can click on any failed action and see the request and response data in appropriate tabs.

### Run JMeter actions via GUI
1. Open JMeter UI as described in [README.md](../../app/util/jmeter/README.md).
1. Enable the `View Results Tree` controller and click `Run` the test scenario. 

### Comparing different runs
Navigate to the `reports_generation` folder and follow README.md instructions to generate side-by-side comparison charts.
