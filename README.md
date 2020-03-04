# Data Center App Performance Toolkit

This is FindOuts fork of https://github.com/atlassian/dc-app-performance-toolkit - see original REAME there.

The pytests for DM can be run either directly with:

    git clone https://github.com/findout/dc-app-performance-toolkit fo-dcapt
    cd fo-dcapt
    cd app
    pytest pytests

or in the Taurus test suite with

    docker run --rm -it --net="host" -v ${PWD}:/bzt-configs -v ${PWD}/results:/tmp/artifacts dagrende/taurus:v1 jira.yml
    
alternativ when running on windows bash give explicit path

    winpty docker run --rm -it --net="host" -v //c/dc-app-performance/dc-app-performance-toolkit/app:/bzt-configs -v //c/dc-app-performance/dc-app-performance-toolkit/app/result:/tmp/artifacts dagrende/taurus:v1 jira.yml

## Building the taurus test tool docker image

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


## Useful links for test writing

* pytest - https://docs.pytest.org/en/latest/contents.html
* requests - https://requests.readthedocs.io/en/master/user/quickstart/#response-headers
* jira rest api authentication - https://community.atlassian.com/t5/Jira-questions/How-to-authenticate-to-Jira-REST-API/qaq-p/814987
