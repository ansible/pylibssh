#!/bin/bash
set -xe

unset RELEASE

# Get script directory
MY_DIR=$(dirname "${BASH_SOURCE[0]}")

# Get build utilities
source $MY_DIR/build_utils.sh

PERL_SHA256="e6c185c9b09bdb3f1b13f678999050c639859a7ef39c8cad418448075f5918af"
PERL_VERSION="5.24.1"

if [[ "$1" =~ "^manylinux1_*" ]]; then
  fetch_source "perl-${PERL_VERSION}.tar.gz" "https://www.cpan.org/src/5.0"
  check_sha256sum "perl-${PERL_VERSION}.tar.gz" ${PERL_SHA256}

  tar zxf perl-$PERL_VERSION.tar.gz && \
      cd perl-$PERL_VERSION && \
      ./Configure -des -Dprefix=/opt/perl && \
      make -j && make install
fi
