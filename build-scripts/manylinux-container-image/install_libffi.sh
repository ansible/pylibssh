#!/bin/bash
set -xe

unset RELEASE

# Get script directory
MY_DIR=$(dirname "${BASH_SOURCE[0]}")

# Get build utilities
source $MY_DIR/build_utils.sh

LIBFFI_SHA256="bc9842a18898bfacb0ed1252c4febcc7e78fa139fd27fdc7a3e30d9d9356119b"
LIBFFI_VERSION="3.4.8"

fetch_source "libffi-${LIBFFI_VERSION}.tar.gz" "https://github.com/libffi/libffi/releases/download/v${LIBFFI_VERSION}/"
check_sha256sum "libffi-${LIBFFI_VERSION}.tar.gz" ${LIBFFI_SHA256}
tar zxf libffi-${LIBFFI_VERSION}.tar.gz

pushd libffi*/
if [[ "$1" =~ '^manylinux1_.*$' ]]; then
  STACK_PROTECTOR_FLAGS="-fstack-protector --param=ssp-buffer-size=4"
else
  STACK_PROTECTOR_FLAGS="-fstack-protector-strong"
fi
./configure CFLAGS="-g -O2 $STACK_PROTECTOR_FLAGS -Wformat -Werror=format-security"
make install
popd
rm -rf libffi*
