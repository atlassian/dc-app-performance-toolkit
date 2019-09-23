## Reports generator - tool that creates aggregated .csv files and charts
Before you start, make sure you have installed Python packages from `jira/requirements.txt`.

Otherwise, run the `pip install -r requirements.txt` command from `jira` directory to install necessary packages to your virtual environment.

To create reports, run the <br>
`python csv_chart_generator.py [performance_profile.yml or scale_profile.yml]` command from the `jira/util/reports_generation` folder.

The aggregated .csv files and charts are stored in the `jira/results/reports` directory.
Before run, you should edit `performance_profile.yml` or `scale_profile.yml` and set appropriate `fullPath` values. 

**Configuration**
- `column_name` - means column from `results.csv` to comparison.
- `run_name` - label for specific run.
- `fullPath` -  the full path to result folder of specific run. Tool will look for result.csv file in this folder<br>
- `index_col` - index column
- `title` - chart title. Also this value is used to generate file name
- `image_height_px` - chart image height in pixels
- `image_width_px` - chart image width in pixels