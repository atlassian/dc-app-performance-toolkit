# name: atlassian/dcapt
# working dir: dc-app-performance-toolkit
# build: docker build -t atlassian/dcapt .
# bzt run: docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt jira.yml
# interactive run: docker run -it --entrypoint="/bin/bash" -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt

FROM python:3.11-slim-bullseye

ENV APT_INSTALL="apt-get -y install --no-install-recommends"

ARG CHROME_VERSION="latest"

ENV CHROME_LATEST_URL="https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
ENV CHROME_VERSION_URL="https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb"

RUN apt-get -y update \
  && $APT_INSTALL vim git openssh-server wget openjdk-11-jdk \
  && python -m pip install --upgrade pip \
  && apt-get clean

RUN if [ "$CHROME_VERSION" = "latest" ]; then wget -O google-chrome.deb $CHROME_LATEST_URL; else wget -O google-chrome.deb $CHROME_VERSION_URL; fi \
  && $APT_INSTALL ./google-chrome.deb \
  && rm -rf ./google-chrome.deb

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN rm -rf /root/.bzt/jmeter-taurus/

WORKDIR /dc-app-performance-toolkit/app

ENTRYPOINT ["bzt", "-o", "modules.console.disable=true"]
