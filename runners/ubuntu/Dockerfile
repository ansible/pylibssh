ARG RELEASE
FROM ubuntu:${RELEASE}

# Increment this to blow away the docker cache
ENV CACHE_BUSTER 1

ENV DEBIAN_FRONTEND noninteractive

# This is needed because otherwise `sys.getfilesystemencoding()` returns
# "ANSI_X3.4-1968".
ENV LANG C.UTF-8

# Also add a travis user
RUN groupadd -g 2000 travis
RUN useradd -u 2000 -g 2000 -m -s /bin/bash travis

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
