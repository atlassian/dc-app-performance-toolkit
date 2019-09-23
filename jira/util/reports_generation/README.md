## Reports generator - tool that creates raw data (aggregates results.csv files) and charts
Before you start, make sure you have installed Python packages from `jira/requirements.txt`.

Otherwise, run the `pip install -r requirements.txt` command from `jira` directory to install necessary packages to your virtual environment.

To create reports, run the <br>
`python reports_generator.py [performance_profile.yml or scale_profile.yml]` command from the `jira/util/reports_generation` folder.

The raw data and chart are stored in the `jira/results/reports` directory.

#####Configuration
```yaml
column_name: "90% Line"
runs:
  - runName: "Node 1"
    fullPath: "/home/$USER/centaurus/jira/results/2019-08-06_17-41-08/results.csv"
  - runName: "Node 2"
    fullPath: "/home/$USER/centaurus/jira/results/2019-08-06_17-41-08/results.csv"
  - runName: "Node 4"
    fullPath: "/home/$USER/centaurus/jira/results/2019-08-07_10-42-52/results.csv"
```
- `column_name` means column from `results.csv` to comparison.
- `run_name` is label for specific run.
- `fullPath` is the full path to file `results.csv` of specific run.<br>

```yaml
index_col: "Action"
title: "Scale Testing"
image_height_px: 1000
image_width_px: 1200
```

- `index_col` - index column
- `title` - chart title. Also this value is used to generate file name
- `image_height_px` - chart image height in pixels
- `image_width_px` - chart image width in pixels