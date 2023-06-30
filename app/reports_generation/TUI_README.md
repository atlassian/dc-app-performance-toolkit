# Text UI Report Generator

## Descripton

It is possible to use TUI tool for report generation. For MacOS it is recommended to use different terminal than the
build-in one for better look and faster responses (for example iTerm2).

```
TUI tool is started in application mode what blocks normal text selectiion with mouse. In most of the terminals you can
hold 'Shift' to re-enable text selection. For OS X: In iTerm, use 'Option' instead of 'Shift'.  In Terminal.app, use 'Fn'.
```


## Usage

### Running the TUI tool
This tool can be run on local machine or on execution environment. When run on execution environment you won't be able to
use `Download tab` as there is no need for this. When report is generated on the execution environment then you need to
download generated report manually using `scp`

- Install and activate the `virtualenv` as described in `dc-app-performance-toolkit/README.md`
- Navigate to the `dc-app-performance-toolkit/app/reports_generation` folder.
- Run the following command:
    ``` bash
    python3 tui_report_generator.py
    ```

### Configuration tab

In this tab you are able to provide configuration for execution environment connection and toolkit path.

#### Execution environment options

- `Username` - username used for ssh connection to execution environment. By default `ubuntu`
- `Hostname` - address used for ssh connection (can be ip or hostname)
- `SSH key path` - path to ssh key used for connection. If ssh key is secured with passphrase, please add it using command:
    ``` bash
    ssh-add path/to/ssh/key.pem
    ```

#### Local configuration options

- `Toolkit path` - path to repository root directory for `dc-apps-performance-toolkit`

### Download test results

Here you are able to download test run results to local machine. Download path is set to `dc-app-performance-toolkit/app/results` by default.
It can be changed according to your needs.

- Click `Connect` button to connect to your execution environment.
- Search for needed test run results.
- Click `Download` button to download selected test results.

Only valid test run results can be downloaded. Verification of test result is done by checking if `summary_results.log` file is available.

### Generate report

This tab allows you to generate all types of reports needed for ECOHELP ticket. It contains `Performance report`, `Scale report` and `Bamboo report`.

- Choose report which you want to generate.
- Set all needed test run result paths by clicking `Choose report path` button next to test result path.
- Click `Generate report` button.
- You can copy last generate report path by clicking `Copy report path` button or by selecting path from logs with the method mentioned at the beginning of this `README`