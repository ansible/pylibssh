FROM centos:7

ARG user=jenkins
ARG group=jenkins
ARG uid=1000
ARG gid=1000

# This is needed because otherwise `sys.getfilesystemencoding()` returns
# "ANSI_X3.4-1968".
ENV LANG C.UTF-8

# Docker pipeline plugin mounts the workspace into the image
# This adds the same uid/gid that we use in the jenkins container
# so getpwuid() won't fail when tox invokes
RUN groupadd -g ${gid} ${group}
RUN useradd -u ${uid} -g ${gid} -m -s /bin/bash ${user}

RUN yum install -y gcc libffi-devel python-devel openssl-devel git which

RUN curl -sSL https://bootstrap.pypa.io/get-pip.py | python

RUN pip install -q tox

USER jenkins
