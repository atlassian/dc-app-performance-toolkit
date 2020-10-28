# name: atlassain/dcapt
# working dir: dc-app-performance-toolkit
# build: docker build -t atlassain/dcapt .
# bzt run: docker run --shm-size=4g -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt jira.yml
# interactive run: docker run -it --entrypoint="/bin/bash" -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt

FROM blazemeter/taurus

ENV APT_INSTALL="apt-get -y install --no-install-recommends"

RUN apt-get -y update \
  && $APT_INSTALL vim git openssh-server  python3.8-dev python3-pip google-chrome-stable \
  && update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1 \
  && python -m pip install --upgrade pip \
  && python -m pip install --upgrade setuptools \
  && apt-get clean

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN rm -rf /root/.bzt/jmeter-taurus/

WORKDIR /dc-app-performance-toolkit/app

ENTRYPOINT ["bzt", "-o", "modules.console.disable=true"]
