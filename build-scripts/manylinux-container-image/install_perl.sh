#!/bin/bash
set -xe

unset RELEASE

curl -O https://www.cpan.org/src/5.0/perl-5.24.1.tar.gz

tar zxf perl-5.24.1.tar.gz && \
    cd perl-5.24.1 && \
    ./Configure -des -Dprefix=/opt/perl && \
    make -j && make install
