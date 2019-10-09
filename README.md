# Data Center App Performance Toolkit 
The Data Center App Performance Toolkit extends [Taurus](https://gettaurus.org/) which is an open source performance framework that executes JMeter and Selenium.

This repository contains Taurus scripts for performance testing of Atlassian Data Center products: Jira, Confluence, and Bitbucket.

At the moment, Jira DC support is in beta. Confluence DC and Bitbucket DC support is coming soon.

## Known issues/limitations
* Supported Jira versions: 
    * Latest platform release: 8.0.3
    * Latest enterprise release: 7.13.6
* The SQL import is flaky. In case of a failure, run it again.

## Installation and set up

#### Dependencies
* Python 3.6+ and pip
* JDK 8
* Google Chrome web browser. 

Please make sure you have a version of Chrome browser that is compatible with [chromedriver](http://chromedriver.chromium.org/downloads) version set in app/%product%.yml file (modules->selenium->chromedriver->version).

If a first part of chromedriver version does not match with a first part of your Chrome browser version, update Chrome browser or set compatible [chromedriver](http://chromedriver.chromium.org/downloads) version in .yml file.  


### macOS/Linux
Make sure that you have [Python](https://www.python.org/downloads/) 3.6+, pip, and [JDK 8](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html) installed:
```
python3 --version
pip --version
java -version
```

We recommend using virtualenv for Taurus.

1. Install virtualenv with pip:
```
pip install virtualenv
```
2. Create new virtual env with python3:
```
virtualenv venv -p python3
```
3. Activate virtual env:
```
source venv/bin/activate
```
4. Install bzt:
```
pip install bzt==1.13.8
```
5. Install dependencies:
```
cd app
pip install -r requirements.txt
```


### Windows
#### Installing Taurus manually
Make sure you have [Python](https://www.python.org/downloads/) 3.6+, pip, and [JDK 8](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html) installed:
```
python --version or python3 --version
pip --version
java -version
Microsoft Visual C++ 14
```

Make sure you have Visual Studio build tool v14.22 installed. 
Otherwise, download it from [Microsoft Visual C++ Build Tools:](https://visualstudio.microsoft.com/downloads) and do the following:
1. Select **Tools for Visual Studio 2019**.
2. Download and run **Build Tools for Visual Studio 2019**.
3. Select the **C++ build tools** check box.
4. Select the **MSVC v142 - VS 2019 C++ x64/x86 build tools (v14.22)** check box (clear all the others).
5. Click **Install**.


We recommend using virtualenv for Taurus.

1. Install virtualenv with pip:
```
pip install virtualenv
```
2. Create new virtual env with python3:
```
virtualenv venv -p python
```
3. Activate virtual env:
```
venv\Scripts\activate
```
4. Install bzt:
```
pip install bzt==1.13.8
```
5. Install dependencies:
```
cd app
pip install -r requirements.txt
```

#### Installing Taurus with prebuilt installer
Download an [installer](https://gettaurus.org/builds/TaurusInstaller_1.13.8_x64.exe) and run it.
It will install local Python 3.6 and Taurus with all its dependencies.

`bzt-pip` is a wrapper for pip that can be used to install packages.

Install dependencies:
```
cd app
bzt-pip install setuptools wheel
bzt-pip install -r requirements.txt
```

## Additional info
Official Taurus installation instructions are located [here](https://gettaurus.org/docs/Installation/).

## Running Taurus
Navigate to product folder and follow README.md instructions.
