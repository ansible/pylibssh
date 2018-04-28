ARG RELEASE
FROM ubuntu:${RELEASE}

ARG user=jenkins
ARG group=jenkins
ARG uid=1000
ARG gid=1000

# Increment this to blow away the docker cache
ENV CACHE_BUSTER 1

ENV DEBIAN_FRONTEND noninteractive

# This is needed because otherwise `sys.getfilesystemencoding()` returns
# "ANSI_X3.4-1968".
ENV LANG C.UTF-8

# Docker pipeline plugin mounts the workspace into the image
# This adds the same uid/gid that we use in the jenkins container
# so getpwuid() won't fail when tox invokes
RUN groupadd -g ${gid} ${group}
RUN useradd -u ${uid} -g ${gid} -m -s /bin/bash ${user}

RUN apt-get -qq update && apt-get install -qq -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python-dev \
    python3-dev \
    git \
    curl \
    libenchant-dev \
    tzdata

RUN curl -sSL https://bootstrap.pypa.io/get-pip.py | python

RUN pip install -q tox

USER jenkins
