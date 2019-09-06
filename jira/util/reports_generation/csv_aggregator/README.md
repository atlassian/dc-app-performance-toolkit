##.csv report aggregator
The `jira/results` folder contains folders with results for different performance runs (e.g. run with or without app, run against one/two/four nodes Jira DataCenter). <br>
Each folder under `jira/results` contains `results.csv` file with aggregated report.<br>
There are two `.yml` files in the `jira/util/csv_aggregator/` directory: `scale_profile.yml` and `performance_profile.yml` <br>
Config file `scale_profile.yml` contains next fields (e.g. below)
```
column_name: "90% Line"
runs:
  - runName: "Node 1"
    fullPath: "/home/$USER/dc-app-performance-toolkit/jira/results/2019-08-06_17-41-08"
  - runName: "Node 2"
    fullPath: "/home/$USER/dc-app-performance-toolkit/jira/results/2019-08-06_17-41-08"
  - runName: "Node 4"
    fullPath: "/home/$USER/dc-app-performance-toolkit/jira/results/2019-08-07_10-42-52"
```
- `column_name` means column from `results.csv` to comparison.
- `run_name` is label for specific run.
- `fullPath` is the full path to directory with `results.csv` aggregated report for specific run.<br>

Run script using the following command:<br>
`python csv_aggregator [scale_profile.yml or performance_profile.yml]`
 