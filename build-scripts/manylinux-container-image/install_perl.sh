#!/bin/bash
set -xe

unset RELEASE

PERL_VERSION=5.24.1
curl -O https://www.cpan.org/src/5.0/perl-$PERL_VERSION.tar.gz

tar zxf perl-$PERL_VERSION.tar.gz && \
    cd perl-$PERL_VERSION && \
    ./Configure -des -Dprefix=/opt/perl && \
    make -j && make install
