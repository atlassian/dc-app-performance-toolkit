## CSV report aggregator and chart generation tool
Before you start, make sure you have installed Python packages from `jira/requirements.txt`.

Otherwise, run the `pip install -r requirements.txt` command from `jira` directory to install necessary packages to your virtual environment.

To create aggregated csv report and chart with one command (recommended), run the <br> 
`python csv_chart_generator.py [performance_profile.yml or scale_profile.yml]` command from the `jira/util/reports_generation` folder.

To create aggregated csv report or chart separately:
* To create only an aggregated csv report, run the <br>
`python csv_aggregator.py [perfomance_profile.yml or scale_profile.yml]` command from the `jira/util/reports_generation/csv_aggregator` folder.

* To create only a chart based on already created aggregated csv report, run the <br>
`python csv_chart_generator.py [perfomance_profile.yml or scale_profile.yml]` command from the `jira/util/reports_generation/chart_generator` folder.

The aggregated csv report and chart are stored in the jira/util/reports_generation/results directory.
