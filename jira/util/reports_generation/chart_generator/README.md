##Chart Generator
Creates chart from aggregated csv file. This csv file you can get by using csv_aggregator<br>
Input csv example:
```text
Action,Node 1,Node 2,Node 4
jmeter_login_and_view_dashboard,2989,2913,2943
jmeter_view_issue,1708,1704,1710
jmeter_search_jql,2566,2439,2461
jmeter_load_first_issue,492,487,491
```

#####Configuration
```yaml
csv_path: ""
index_col: "Action"
title: "Scale Testing"
image_height_px: 1000
image_width_px: 1200
```

- `aggregated_csv_path` - absolute or relative path to csv file. Preferred is absolute. 
- `index_col` - index column
- `title` - chart title. Also this value is used to generate file name
- `image_height_px` - chart image height in pixels
- `image_width_px` - chart image width in pixels


#####Running
To run script you need installed python and dependencies from `centaurus/jira/requirements.txt`<br>
Run script using the following command:
```text
python chart_generator.py <yml config file path (absolute or relative)>
```
