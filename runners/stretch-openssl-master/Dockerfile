FROM debian:stretch

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

RUN apt-get -qq update && apt-get install -qq -y \
    build-essential \
    libffi-dev \
    python-dev \
    python3-dev \
    git \
    curl

RUN curl -sSL https://bootstrap.pypa.io/get-pip.py | python

RUN pip install -q tox

WORKDIR /root

RUN git clone --depth=1 https://github.com/openssl/openssl

RUN cd openssl && \
    ./config --prefix=/opt/pyca/cryptography/openssl \
             --openssldir=/opt/pyca/cryptography/openssl no-comp && \
    make depend && \
    make -j4 && \
    make install && \
    cd .. && \
    rm -rf openssl

USER jenkins
