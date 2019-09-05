# Data Center App Performance Toolkit 
The Data Center App Performance Toolkit extends [Taurus](https://gettaurus.org/) which is an open source performance framework that uses JMeter and selenium.

This repository contains Taurus scripts for performance testing Atlassian's Data Center products: Jira, Confluence and Bitbucket.

At the moment Jira DC support is in Beta. Confluence DC and Bitbucket DC support is coming soon.

## Known Issues/Limitations
* Jira DC support is in Alpha.
* Jira only supports version 8.0.3.
* There is a critical bug in the Taurus Windows Prebuilt Installer. This means for Window toolkit should be installed manually.
* The SQL import appears to be a little flaky. If you are getting errors the first time, try it again and it will work.

## Installation and set up

#### Dependencies
* Python 3.6+ and pip
* JDK 8
* Google Chrome web browser version 76

### macOS / Linux
Please make sure that you have [Python](https://www.python.org/downloads/) 3.6+, pip and [JDK 8](https://www.java.com/download/) installed:
```
python3 --version
pip --version
java -version
```
Check that Chrome browser version is 76.

We recommend using virtualenv for Taurus.

Install virtualenv with pip:
```
pip install virtualenv
```
Create new virtual env with python3:
```
virtualenv venv -p python3
```
Activate virtualenv:
```
source venv/bin/activate
```
Install bzt:
```
pip install bzt==1.13.8
```
Install dependencies:
```
cd jira
pip install -r requirements.txt
```


### Windows
There are two ways of installing Taurus on Windows.
One way is to use the prebuilt installer that will install latest Taurus on your PC including local Python 3.6 and all its dependencies.
However, if you already have Python installed, you can install Taurus manually with pip, Python package manager.

#### Installing Taurus Manually
Please make sure that you have [Python](https://www.python.org/downloads/) 3.6+, pip and [JDK 8](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html) installed:
```
python --version or python3 --version
pip --version
java -version
Microsoft Visual C++ 14
```
Check that Chrome browser version is 76.

Make sure you have Visual Studio build tool v14.22. 
You can get it with [Microsoft Visual C++ Build Tools:](https://visualstudio.microsoft.com/downloads)
-> Tools for Visual Studio 2019
-> Build Tools for Visual Studio 2019
-> Download and Run
-> C++ build tools
-> MSVC v142 - VS 2019 C++ x64/x86 build tools (v14.22)
-> Install


We recommend using virtualenv for Taurus.

Install virtualenv with pip:
```
pip install virtualenv
```
Create new virtual env with python3:
```
virtualenv venv -p python
```
Activate virtualenv:
```
venv\Scripts\activate
```
Install bzt:
```
pip install bzt==1.13.8
```
Install dependencies:
```
cd jira
pip install -r requirements.txt
```

#### Installing Taurus With Prebuilt Installer
Download an [installer](https://gettaurus.org/builds/TaurusInstaller_1.13.8_x64.exe) and run it on your system.
It will install local Python 3.6 and Taurus with all its dependencies.

`bzt-pip` is a wrapper for pip that can be used to install packages.

Install dependencies:
```
cd jira
bzt-pip install setuptools wheel
bzt-pip install -r requirements.txt
```

## Additional info
Official Taurus installation instructions could be found [here](https://gettaurus.org/docs/Installation/).

## Running Taurus
Navigate to product folder and follow README.md instructions.
