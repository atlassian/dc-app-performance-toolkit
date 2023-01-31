# Data Center App Performance Toolkit 
The Data Center App Performance Toolkit extends [Taurus](https://gettaurus.org/) which is an open source performance framework that executes JMeter and Selenium.

This repository contains Taurus scripts for performance testing of Atlassian Data Center products: Jira, Jira Service Management, Confluence, Bitbucket and Crowd.

## Supported versions
* Supported Jira versions: 
    * Jira [Long Term Support release](https://confluence.atlassian.com/enterprise/atlassian-enterprise-releases-948227420.html): `8.20.15` and `9.4.0`

* Supported Jira Service Management versions: 
    * Jira Service Management [Long Term Support release](https://confluence.atlassian.com/enterprise/atlassian-enterprise-releases-948227420.html): `4.20.15` and `5.4.0`
    
* Supported Confluence versions:
    * Confluence [Long Term Support release](https://confluence.atlassian.com/enterprise/atlassian-enterprise-releases-948227420.html): `7.19.2`, `7.13.7`  and `8.0.0` platform release

* Supported Bitbucket Server versions:
    * Bitbucket Server [Long Term Support release](https://confluence.atlassian.com/enterprise/atlassian-enterprise-releases-948227420.html): `7.21.7`, `7.17.13`, and `8.0.5` platform release.

* Supported Crowd versions:
    * Crowd [release notes](https://confluence.atlassian.com/crowd/crowd-release-notes-199094.html): `5.0.2`
  
* Supported Bamboo versions:
    * Bamboo [release notes](https://confluence.atlassian.com/bamboo/bamboo-release-notes-671089224.html): `8.1.3`
  
## Support
In case of technical questions, issues or problems with DC Apps Performance Toolkit, contact us for support in the [community Slack](http://bit.ly/dcapt_slack) **#data-center-app-performance-toolkit** channel.

## Installation and set up

#### Dependencies
* Python 3.8, 3.9, 3.10 or 3.11 and pip
* JDK 11
* Google Chrome web browser
* Git client (only for Bitbucket DC)

Please make sure you have a version of Chrome browser that is compatible with [ChromeDriver](http://chromedriver.chromium.org/downloads) version set in app/$product.yml file (modules->selenium->chromedriver->version).

If a first part of ChromeDriver version does not match with a first part of your Chrome browser version, update Chrome browser or set compatible [ChromeDriver](http://chromedriver.chromium.org/downloads) version in .yml file.

### macOS setup
Make sure that you have:
* [Python](https://www.python.org/downloads/) (see [dependencies](#dependencies) section for supported versions)
* pip
* [JDK 11](https://www.oracle.com/java/technologies/downloads/#java11) installed
* XCode Command Line Tools
* Google Chrome web browser
```
python3 --version
pip --version
java -version
# command to check if XCode Command Line Tools installed
xcode-select --print-path
# or command to install if XCode Command Line Tools
xcode-select --install
```
For Bitbucket DC check that [Git](https://git-scm.com/downloads) is installed:
```
git --version
```

We recommend using [virtualenv](https://virtualenv.pypa.io/en/latest/) for Taurus.

1. Install virtualenv with pip:
```
pip install virtualenv
```
2. Create new virtual env with python3:
```
virtualenv venv -p full_path_to_python # e.g. use `which python3.11` to find the path
```
3. Activate virtual env:
```
source venv/bin/activate
```
4. Install dependencies:
```
pip install -r requirements.txt
```

### Linux setup
Make sure that you have:
* [Python](https://www.python.org/downloads/) (see [dependencies](#dependencies) section for supported versions)
* pip
* [JDK 11](https://www.oracle.com/java/technologies/downloads/#java11) installed
* Python developer package (e.g. `python3.9-dev` package for Python3.9)
* Google Chrome web browser
```
python3 --version
pip --version
java -version
```
For Bitbucket DC check that [Git](https://git-scm.com/downloads) is installed:
```
git --version
```
We recommend using [virtualenv](https://virtualenv.pypa.io/en/latest/) for Taurus. See example setup below.

## Example setup for clean Ubuntu 20.04
JDK setup (if missing):
```
sudo apt-get update
sudo apt-get install -y openjdk-11-jre-headless
```
Chrome setup (if missing):
```
sudo apt-get update
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt-get install -y ./google-chrome-stable_current_amd64.deb
```
Python and virtualenv setup:
```
sudo apt-get update
sudo apt-get -y install python3.9-dev python3-pip virtualenv
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1
virtualenv venv -p /usr/bin/python
source venv/bin/activate
pip install -r requirements.txt
```

### Windows setup
#### Installing Taurus manually
Make sure you have [Python](https://www.python.org/downloads/) (see [dependencies](#dependencies) section for supported versions), pip, and [JDK 11](https://www.oracle.com/java/technologies/downloads/#java11) installed:
```
python --version or python3 --version
pip --version
java -version
Microsoft Visual C++ 14
Windows 10 SDK
```
For Bitbucket Server check that [Git](https://git-scm.com/downloads) is installed:
```
git --version
```

Make sure you have Visual Studio build tool v14.22 installed. 
Otherwise, download it from [Microsoft Visual C++ Build Tools:](https://visualstudio.microsoft.com/downloads) and do the following:
1. Select **Tools for Visual Studio 2019**.
2. Download and run **Build Tools for Visual Studio 2019**.
3. Select the **C++ build tools** check box.
4. Select the **MSVC v142 - VS 2019 C++ x64/x86 build tools (v14.22)** check box (clear all the others).
5. Click **Install**.

Setup [Windows 10 SDK](https://developer.microsoft.com/en-us/windows/downloads/windows-10-sdk/)

We recommend using [virtualenv](https://virtualenv.pypa.io/en/latest/) for Taurus.
1. Install virtualenv with pip:
```
pip install virtualenv
```
2. Create new virtual env with python3:
```
virtualenv venv -p full_path_to_python # e.g. use `where python` to find the path to correct python
```
3. Activate virtual env:
```
venv\Scripts\activate
```
4. Install dependencies:
```
pip install -r requirements.txt
```

## Upgrading the toolkit
Get latest codebase from master branch:
```
git pull
```
Activate virtual env for the toolkit and install latest versions of libraries:
```
pip install -r requirements.txt
```

## Additional info
Official Taurus installation instructions are located [here](https://gettaurus.org/docs/Installation/).

## Analytics
The Data Center App Performance Toolkit includes some simple usage analytics.  
We collect this data to better understand how the community is using the Performance Toolkit, and to help us plan our roadmap.
When a performance tests is completed we send one HTTP POST request with analytics.

The request include the following data, and will in no way contain PII (Personally Identifiable Information).
- application under test (Jira/Confluence/Bitbucket)
- timestamp of performance toolkit run
- performance toolkit version
- operating system
- `concurrency` and `test_duration` from `$product.yml` file
- actual run duration
- executed action names and success rates
- unique user identifier (non PII)

To help us continue improving the Toolkit, we’d love you to keep these analytics enabled in testing, staging, and production. If you don’t want to send us analytics, you can turn off the `allow_analytics` toggle in `$product.yml` file.

## Running Taurus
Navigate to [docs](docs) folder and follow instructions.
