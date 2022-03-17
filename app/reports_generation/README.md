## Reports generator - a tool that creates an aggregated .csv file, chart and summary report from multiple run results.
Before you start, make sure you have installed Python packages from [requirements.txt](../../requirements.txt).

Otherwise, run the `pip install -r requirements.txt` command from DCAPT [root](../..) directory to install necessary packages to your virtual environment.

To create reports, run the <br>
`python csv_chart_generator.py [performance_profile.yml or scale_profile.yml]` command from the `reports_generation` folder.

The aggregated .csv files, charts and summary report are stored in the `results/reports` directory.
Before run, you should edit `performance_profile.yml` or `scale_profile.yml` and set appropriate `fullPath` values. 

**Configuration**
- `column_name` - column name from results.csv used for aggregation
- `runName` - label for specific run
- `runType` - label for run type
- `fullPath` -  the full path to result folder of specific run
- `index_col` - index column
- `title` - chart title (also this value is used to generate file name)
- `image_height_px` - chart image height in pixels
- `image_width_px` - chart image width in pixels
- `check_actions_count` - [optional] check if actions count is the same for all runs. Default value is `true`
- `judge` - [optional] compare results by measuring performance deviation of experiment version from baseline
