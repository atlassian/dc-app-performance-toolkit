# name: atlassian/dcapt
# working dir: dc-app-performance-toolkit
# build: docker build -t atlassian/dcapt .
# bzt run: docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt jira.yml
# interactive run: docker run -it --entrypoint="/bin/bash" -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt

FROM python:3.13-slim-bookworm

ENV APT_INSTALL="apt-get -y install --no-install-recommends"

ARG CHROME_VERSION="latest"
ARG INCLUDE_BZT_TOOLS="false"

ENV CHROME_LATEST_URL="https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
ENV CHROME_VERSION_URL="https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb"

RUN apt-get -y update \
  && $APT_INSTALL vim git openssh-server wget \
  && python -m pip install --upgrade pip \
  && apt-get clean

RUN wget https://download.oracle.com/java/21/latest/jdk-21_linux-x64_bin.deb \
  && $APT_INSTALL ./jdk-21_linux-x64_bin.deb \
  && rm -rf ./jdk-21_linux-x64_bin.deb

RUN if [ "$CHROME_VERSION" = "latest" ]; then wget -O google-chrome.deb $CHROME_LATEST_URL; else wget -O google-chrome.deb $CHROME_VERSION_URL; fi \
  && $APT_INSTALL ./google-chrome.deb \
  && rm -rf ./google-chrome.deb

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN if [ "$INCLUDE_BZT" = "true" ]; then \
      wget https://blazemeter-tools.s3.us-east-2.amazonaws.com/bzt.tar.gz -O /tmp/bzt.tar.gz && \
      tar -xzf /tmp/bzt.tar.gz -C /root && \
      rm /tmp/bzt.tar.gz; \
    fi

WORKDIR /dc-app-performance-toolkit/app

ENTRYPOINT ["bzt", "-o", "modules.console.disable=true"]
