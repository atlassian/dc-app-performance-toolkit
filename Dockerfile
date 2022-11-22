# name: atlassian/dcapt
# working dir: dc-app-performance-toolkit
# build: docker build -t atlassian/dcapt .
# bzt run: docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt jira.yml
# interactive run: docker run -it --entrypoint="/bin/bash" -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt

FROM blazemeter/taurus:1.16.18

ENV APT_INSTALL="apt -y install --no-install-recommends"
RUN apt -y update \
  && $APT_INSTALL vim git python3.9-dev python3-pip wget \
  && update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1 \
  && python -m pip install --upgrade pip \
  && python -m pip install --upgrade setuptools \
  && apt clean

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
  && $APT_INSTALL ./google-chrome-stable_current_amd64.deb \
  && rm -rf ./google-chrome-stable_current_amd64.deb

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN rm -rf /root/.bzt/jmeter-taurus/

WORKDIR /dc-app-performance-toolkit/app

ENTRYPOINT ["bzt", "-o", "modules.console.disable=true"]
