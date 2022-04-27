#!/bin/bash
set -xe

unset RELEASE

# Get script directory
MY_DIR=$(dirname "${BASH_SOURCE[0]}")

# Get build utilities
source $MY_DIR/build_utils.sh

LIBFFI_SHA256="72fba7922703ddfa7a028d513ac15a85c8d54c8d67f55fa5a4802885dc652056"
LIBFFI_VERSION="3.3"

fetch_source "libffi_${LIBFFI_VERSION}.orig.tar.gz" "https://mirrors.ocf.berkeley.edu/debian/pool/main/libf/libffi"
check_sha256sum "libffi_${LIBFFI_VERSION}.orig.tar.gz" ${LIBFFI_SHA256}
tar zxf libffi_${LIBFFI_VERSION}.orig.tar.gz

pushd libffi*/
if [[ "$1" =~ '^manylinux1_.*$' ]]; then
  PATH=/opt/perl/bin:$PATH
  STACK_PROTECTOR_FLAGS="-fstack-protector --param=ssp-buffer-size=4"
else
  STACK_PROTECTOR_FLAGS="-fstack-protector-strong"
fi
./configure CFLAGS="-g -O2 $STACK_PROTECTOR_FLAGS -Wformat -Werror=format-security"
make install
popd
rm -rf libffi*
