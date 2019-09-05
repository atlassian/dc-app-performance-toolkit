##CSV report aggregator and chart generation tool
Before you start, make sure you have installed Python packages from `centaurus/jira/requirements.txt`. <br>
Otherwise, run:
`pip install -r requirements.txt` from `centaurus/jira` directory to install necessary packages to your virtual environment.
<br>
There are few options to create report are available:
1) To create aggregated csv report and chart based on report you can run <br>
 `python csv_chart_generator.py [performance_profile.yml or scale_profile.yml]` from `centaurus/jira/util/reports_generation`
2) To create just csv report you can run <br>
`python csv_aggregator.py [perfomance_profile.yml or scale_profile.yml]` from `centaurus/jira/util/reports_generation/csv_aggregator`
3) To create chart based on already created aggregated csv report you can run <br>
`python csv_chart_generator.py [perfomance_profile.yml or scale_profile.yml]` from `centaurus/jira/util/reports_generation/chart_generator`

<b>Example 1.</b> Create scalability aggregated report and chart based on report <br>
 There are two config files under the `centaurus/jira/util/reports_generation`: <br>
 - `scale_profile.yml`:
```yaml
column_name: "90% Line" - column name to compare from results.csv
runs:
    # fullPath should contain full path to directory with results.csv for the specific run. E.g. /home/$USER/centaurus/jira/results/2019-08-06_17-41-08
  - runName: "Node 1"
    fullPath: "" 
  - runName: "Node 2"
    fullPath: ""
  - runName: "Node 4"
    fullPath: ""

# Chart generation configs
index_col: "Action"
title: "Scale Testing"
image_height_px: 1000
image_width_px: 1200

```

To get scalability report run next command from `centaurus/jira/util/reports_generation` directory: 
```
python csv_chart_generator.py scale_profile.yml
```
You can find aggregated csv report and chart in `centaurus/jira/util/reports_generation/results` directory.