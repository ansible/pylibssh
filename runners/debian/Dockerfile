ARG RELEASE
FROM debian:${RELEASE}

# Increment this to blow away the docker cache
ENV CACHE_BUSTER 5

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
    python3-dev \
    git \
    curl \
    libenchant-dev

RUN if grep -q "sid" /etc/debian_version; then apt-get -qq update && apt-get install -qq -y python3-distutils python2-dev; else apt-get install -qq -y python-dev; fi

RUN curl -sSL https://bootstrap.pypa.io/get-pip.py | python3

RUN pip install -q tox

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable
ENV PATH="$HOME/.cargo/bin:$PATH"
