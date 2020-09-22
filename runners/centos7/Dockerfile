FROM centos:7

# Increment this to blow away the docker cache
ENV CACHE_BUSTER 1

# This is needed because otherwise `sys.getfilesystemencoding()` returns
# "ANSI_X3.4-1968".
ENV LANG C.UTF-8

RUN yum install -y gcc libffi-devel python-devel openssl-devel git which

RUN curl -sSL https://bootstrap.pypa.io/get-pip.py | python

RUN pip install -q tox

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable
ENV PATH="/root/.cargo/bin:$PATH"
