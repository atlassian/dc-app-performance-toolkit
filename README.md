# Data Center App Performance Toolkit

This is FindOuts fork of https://github.com/atlassian/dc-app-performance-toolkit - see original REAME there.

The pytests for DM can be run either directly with:

    git clone https://github.com/findout/dc-app-performance-toolkit fo-dcapt
    cd fo-dcapt
    cd app
    pytest pytests

or in the Taurus test suite with

    docker run --rm -it --net="host" -v ${PWD}:/bzt-configs -v ${PWD}/results:/tmp/artifacts dagrende/taurus:v1 jira.yml

## Useful links for test writing

* pytest - https://docs.pytest.org/en/latest/contents.html
* requests - https://requests.readthedocs.io/en/master/user/quickstart/#response-headers
* jira rest api authentication - https://community.atlassian.com/t5/Jira-questions/How-to-authenticate-to-Jira-REST-API/qaq-p/814987
