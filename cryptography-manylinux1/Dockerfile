ARG ARCH
FROM quay.io/pypa/manylinux1_${ARCH}

ARG user=jenkins
ARG group=jenkins
ARG uid=1000
ARG gid=1000

MAINTAINER Python Cryptographic Authority

# Docker pipeline plugin mounts the workspace into the image
# This adds the same uid/gid that we use in the jenkins container
# so files written to a mounted volume will be readable by
# jenkins outside the container
RUN groupadd -g ${gid} ${group}
RUN useradd -u ${uid} -g ${gid} -m -s /bin/bash ${user}

WORKDIR /root
RUN curl -O https://www.cpan.org/src/5.0/perl-5.24.1.tar.gz
RUN tar zxf perl-5.24.1.tar.gz && \
    cd perl-5.24.1 && \
    ./Configure -des -Dprefix=/opt/perl && \
    make -j4 && make install
ADD install_openssl.sh /root/install_openssl.sh
RUN sh install_openssl.sh ${ARCH}

USER jenkins
