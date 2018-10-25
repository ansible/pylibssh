FROM registry.fedoraproject.org/fedora:latest

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
# also add a travis user
RUN groupadd -g 2000 travis
RUN useradd -u 2000 -g 2000 -m -s /bin/bash travis

RUN dnf install -y gcc redhat-rpm-config libffi-devel python-devel \
    python3-devel openssl-devel git findutils which

# This is a workaround for a Jenkins docker workflow plugin bug
# It can be removed when https://issues.jenkins-ci.org/browse/JENKINS-40101
# is resolved.
RUN dnf install -y procps-ng

RUN curl -sSL https://bootstrap.pypa.io/get-pip.py | python

RUN pip install -q tox

USER jenkins
