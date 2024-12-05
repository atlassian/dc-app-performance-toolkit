# Dependency part:

```
export NVDAPIKEY=(Get one from https://nvd.nist.gov/developers/request-an-api-key)
atlas-mvn verify
atlas-mvn dependency:tree -DoutputType=dot -DoutputFile=maven_dependency_tree.gv
```

# Test part:

Download https://github.com/collabsoft-net/dcdx/blob/next/src/commands/apt.ts project
Build with yarn install & yarn run build
Get a new trial license for Conf/Jira and remove lines from it
Replace the license in lib/commands/apt.js
Create a new AWS key for the test
Run the apt command `node apt.js` and follow on screen prompts. Take note of the environment name and the product name

# Tear down part:

`node apt.js teardown --product jira --environment dc-jira-test-2024`

And it needs the default dc-app-performance-toolkit directory

# Report part:

Put Run1 and Run2 in the same folder (the same for Run3, Run4 and Run5) in the ~/.dcdx/apt folder then run

`node apt.js  report --type performance --ts 2024-12-04-18-59 --cwd /Users/mohamedin/Downloads/dc-app-performance-toolkit`
where 2024-12-03-14-06 is the timestamp of the first run (folder name in ~/.dcdx/apt which contains the runs)
Report is generated in the same folder as the runs. (performance needs run1 and run2 in the same folder, scalability needs run3, run4 and run5 in the same folder)

# Notes:

- Don't change the default run time (45m)
- Get two versions of the dc-app-performance-toolkit: The default one from (https://github.com/atlassian/dc-app-performance-toolkit) and ours (https://github.com/jgraph/dc-app-performance-toolkit) after merging with the latest changes from the default one. Ours has the app specific changes.
- Starting from run2, manually install our app
- If the command fails, run it again uisng something like `node apt.js run1 --product confluence --cwd /Users/mohamedin/Downloads/dc-app-performance-toolkit --environment dc-conf-test-24` and continue with the rest of the runs manually (run2, run3, run4, run5) then report generation
- If it fails due to terraform errors (e.g, cannot update the stack), it's better to delete the stack and start from scratch using the teardown command (e.g, if the performance test was done, start from the scalability test with a new environment name [run4] and remember to install the app and reindex)