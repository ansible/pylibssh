ARG RELEASE
FROM ubuntu:${RELEASE}

# Increment this to blow away the docker cache
ENV CACHE_BUSTER 2

ENV DEBIAN_FRONTEND noninteractive

# This is needed because otherwise `sys.getfilesystemencoding()` returns
# "ANSI_X3.4-1968".
ENV LANG C.UTF-8

RUN apt-get -qq update && apt-get install -qq -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    git \
    curl \
    tzdata

RUN curl -sSL https://bootstrap.pypa.io/get-pip.py | python3

RUN pip install tox coverage

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable --profile minimal
ENV PATH="/root/.cargo/bin:$PATH"
