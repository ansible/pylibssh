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

RUN apt-get -qq update && apt-get install -qq -y \
    build-essential \
    libffi-dev \
    python-dev \
    git \
    curl

ARG LIBRE_VERSION

ADD https://ftp.openbsd.org/pub/OpenBSD/LibreSSL/libressl-${LIBRE_VERSION}.tar.gz .
RUN tar zxf libressl-${LIBRE_VERSION}.tar.gz

WORKDIR libressl-${LIBRE_VERSION}
RUN ./config -Wl -Wl,-Bsymbolic-functions -fPIC shared --prefix=/usr/local/libressl
RUN make -j4 install

WORKDIR ../

RUN rm -rf libressl-${LIBRE_VERSION} libressl-${LIBRE_VERSION}.tar.gz

RUN curl -sSL https://bootstrap.pypa.io/get-pip.py | python

RUN pip install -q tox

USER jenkins
