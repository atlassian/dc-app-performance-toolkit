## Start JMeter UI
Util script to launch JMeter UI with all settings from `.yml` file.
Useful for JMeter debugging or JMeter-based app-specific actions.

1. Make sure you run `bzt your_product.yml` command locally at least once - to automatically install JMeter and Jmeter plugins to local computer.
1. Check that `.yml` file has correct settings of `application_hostname`, `application_protocol`, `application_port`, `application_postfix`, etc.
1. Set desired execution percentage for `standalone_extension`. Default value is `0`, which means that `standalone_extension` action will not be executed.
Similarly, set any desired action percentage to 100 and others to 0, if you want to debug specific action execution.
1. Activate toolkit virtualenv. See [toolkit README](../../../README.md) file for more details.
1. Navigate to `app` folder and run command depending on your application type: 
    ```
    cd app
    python util/jmeter/start_jmeter_ui.py --app jira
    # or
    python util/jmeter/start_jmeter_ui.py --app confluence
    # or
    python util/jmeter/start_jmeter_ui.py --app bitbucket
    # or
    python util/jmeter/start_jmeter_ui.py --app jsm --type agents
    # or
    python util/jmeter/start_jmeter_ui.py --app jsm --type customers
    ```
1. Right-click on `View Results Tree` controller and select `Enable` option.
1. Click `Start` button.
1. Disable `View Results Tree` controller before full-scale results generation.