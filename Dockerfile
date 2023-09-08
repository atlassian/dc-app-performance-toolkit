# name: atlassian/dcapt
# working dir: dc-app-performance-toolkit
# build: docker build -t atlassian/dcapt .
# bzt run: docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt jira.yml
# interactive run: docker run -it --entrypoint="/bin/bash" -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt

FROM python:3.11-slim-bullseye

ENV APT_INSTALL="apt-get -y install --no-install-recommends"

RUN apt-get -y update \
  && $APT_INSTALL vim git openssh-server wget openjdk-11-jdk \
  && python -m pip install --upgrade pip \
  && apt-get clean

# Workaround to deal with broken chrome for testing changes 9/8/2023
RUN wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_114.0.5735.90-1_amd64.deb \
  && $APT_INSTALL ./google-chrome-stable_114.0.5735.90-1_amd64.deb

# Original entry for downloading chrome driver
# RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
#   && $APT_INSTALL ./google-chrome-stable_current_amd64.deb \
#   && rm -rf ./google-chrome-stable_current_amd64.deb

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN rm -rf /root/.bzt/jmeter-taurus/

WORKDIR /dc-app-performance-toolkit/app

ENTRYPOINT ["bzt", "-o", "modules.console.disable=true"]
