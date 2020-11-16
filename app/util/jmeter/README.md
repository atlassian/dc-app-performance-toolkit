## Start JMeter UI
Util script to launch JMeter UI with all settings from `.yml` file.
Useful for JMeter debugging or JMeter-based app-specific actions.

1. Check that `.yml` file has correct settings of `application_hostname`, `application_protocol`, `application_port`, `application_postfix`, etc.
2. Check desired execution percentage for `standalone_extension`. Default value is `0`, which means that `standalone_extension` action will not be executed.
3. Activate virtualenv. See [toolkit README](../../../README.md) file for more details.
4. Navigate to `app` folder and run command depending of your application type: 
```
cd app
python util/jmeter/start_jmeter_ui.py --app jira
# or
python util/jmeter/start_jmeter_ui.py --app confluence
# or
python util/jmeter/start_jmeter_ui.py --app bitbucket
# or
python util/jmeter/start_jmeter_ui.py --app jsm
```