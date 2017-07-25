ARG ARCH
FROM quay.io/pypa/manylinux1_${ARCH}
MAINTAINER Python Cryptographic Authority
# ARCH before FROM is unavailable to later RUN calls so we have to take
# matters into our own hands. https://github.com/moby/moby/issues/34129
ARG ARCH2ELECTRICBOOGALOO
WORKDIR /root
RUN curl -O https://www.cpan.org/src/5.0/perl-5.24.1.tar.gz
RUN tar zxf perl-5.24.1.tar.gz && \
    cd perl-5.24.1 && \
    ./Configure -des -Dprefix=/opt/perl && \
    make -j4 && make install
ADD install_openssl.sh /root/install_openssl.sh
RUN sh install_openssl.sh ${ARCH2ELECTRICBOOGALOO}
