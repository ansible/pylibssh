FROM centos:7

ARG user=jenkins
ARG group=jenkins
ARG uid=1000
ARG gid=1000

# Docker pipeline plugin mounts the workspace into the image
# This adds the same uid/gid that we use in the jenkins container
# so getpwuid() won't fail when tox invokes
RUN groupadd -g ${gid} ${group}
RUN useradd -u ${uid} -g ${gid} -m -s /bin/bash ${user}

RUN yum install -y gcc libffi-devel python-devel openssl-devel git

RUN curl -s -O https://bootstrap.pypa.io/get-pip.py && python get-pip.py && rm get-pip.py

RUN pip install -q tox

USER jenkins
