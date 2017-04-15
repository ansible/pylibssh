# The Debian Dockerfiles can be de-duplicated once
# a docker with support for ARG in FROM is released.
# See: https://github.com/docker/docker/pull/31352
FROM debian:jessie

ARG user=jenkins
ARG group=jenkins
ARG uid=1000
ARG gid=1000

# Docker pipeline plugin mounts the workspace into the image
# This adds the same uid/gid that we use in the jenkins container
# so getpwuid() won't fail when tox invokes
RUN groupadd -g ${gid} ${group}
RUN useradd -u ${uid} -g ${gid} -m -s /bin/bash ${user}

RUN apt-get -qq update


RUN apt-get install -qq -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python-dev \
    python3-dev \
    git \
    curl

RUN curl -s -O https://bootstrap.pypa.io/get-pip.py && python get-pip.py && rm get-pip.py

RUN pip install -q tox

USER jenkins
