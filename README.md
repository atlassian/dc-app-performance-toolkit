# Data Center App Performance Toolkit

This is FindOuts fork of https://github.com/atlassian/dc-app-performance-toolkit - see original REAME there.

The pytests for DM can be run either directly with:

    git clone https://github.com/findout/dc-app-performance-toolkit fo-dcapt
    cd fo-dcapt
    cd app
    pytest pytests
    
## Run tests in docker

or in the Taurus test suite with

    docker run --rm -it --net="host" -v ${PWD}:/bzt-configs -v ${PWD}/results:/tmp/artifacts dagrende/taurus:v1 jira.yml
    
alternativ when running on windows bash give explicit path

    winpty docker run --rm -it --net="host" -v //c/dc-app-performance/dc-app-performance-toolkit/app:/bzt-configs -v //c/dc-app-performance/dc-app-performance-toolkit/app/result:/tmp/artifacts dagrende/taurus:v1 jira.yml

### Building the taurus test tool docker image

Taurus have published the taurus test tool as a docker image with the name Blazemeter/taurus. If you get problems when you run it the reason may be it is built some time ago and their components are outdated.
It is easy to rebuild it yourself:

    git clone git@github.com:Blazemeter/taurus.git
    cd taurus
    docker build -t taurus .
    
Now you can run the test as above, but with the command:

    docker run --rm -it --net="host" -v ${PWD}:/bzt-configs -v ${PWD}/results:/tmp/artifacts taurus jira.yml
    
In addition, you may publish your taurus image, for anyone to run:

    docker tag taurus yourname/taurus:v1
    docker push yourname/taurus:v1

Run it with:

    docker run --rm -it --net="host" -v ${PWD}:/bzt-configs -v ${PWD}/results:/tmp/artifacts yourname/taurus:v1 jira.yml


### Useful links for test writing

* pytest - https://docs.pytest.org/en/latest/contents.html
* requests - https://requests.readthedocs.io/en/master/user/quickstart/#response-headers
* jira rest api authentication - https://community.atlassian.com/t5/Jira-questions/How-to-authenticate-to-Jira-REST-API/qaq-p/814987

## Run tests on an AWS server

    git clone https://github.com/FindOut/dc-app-performance-toolkit.git
    cd dc-app-performance-toolkit
    virtualenv venv -p python3
    source venv/bin/activate
    pip install pytest
    deactivate
    source venv/bin/activate
    pip install -r requirements.txt
    
Now we have an environment with python and pytest using python3 and the required python packages.

### run the DM test suite

In the Jira Datacenter App Perfomance test, one step is to run tests specific for Dependency Map. 

    cd app/pytests

Create initial data specific to DM, like links between random issues and dependency map objects.

    python setup.py
    
Here we should probably re-index Jira.

    Go to  > System.
    Select Advanced > Indexing 
    
Copy the delete instructions for the setup, and find out how man objects have been created

    cp deleteCreatedObjects deleteCreatedObjectsSetup
    wc -l deleteCreatedObjects 
    
Run the DM specific test suite.

    bzt jira-dm.yml
    
Remove DM specific data created during run

    wc -l deleteCreatedObjects
    tail -n +<lines diff> deleteCreatedObjects > deleteDuringRun   
    
Remove DM specific data created by setup.py above.

    pythone cleanupObjCreatedDuringRun.py
    
If you want to remove all objects created of setup and running    

    python cleanup.py


## Extending JMeter tests

GT: If you would like to extend the JMeter tests, the following might help with debugging. From the DC-Performance-Testing slack channel:

```
1. Open JMeter UI from app folder: ~/.bzt/jmeter-taurus/5.2.1/bin/jmeter
2. File->Open-> jira.jmx
3. In Test Plan->Global Variables setup your appication.hostname
4. In Jira -> load profile set perc_standalone_extension to 100
5. Enable View Results Tree
6. Extend stanalone extension with new steps
7. Run Jmeter with Green arrow button and see debug info in View Results Tree
To include variables such as ${project_key} for debugging, you can edit file app/datasets/jira/project_keys.csv . But later on for bzt run, it may be better to edit app/util/data_preparation/jira/prepare-data.py to filter only needed project keys with jql.
