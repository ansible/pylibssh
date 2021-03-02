#!/bin/bash
set -xe

unset RELEASE

LIBFFI_SHA256="72fba7922703ddfa7a028d513ac15a85c8d54c8d67f55fa5a4802885dc652056"
LIBFFI_VERSION="3.3"

function check_sha256sum {
    local fname=$1
    local sha256=$2
    echo "${sha256}  ${fname}" > "${fname}.sha256"
    sha256sum -c "${fname}.sha256"
    rm "${fname}.sha256"
}

curl -#O "https://mirrors.ocf.berkeley.edu/debian/pool/main/libf/libffi/libffi_${LIBFFI_VERSION}.orig.tar.gz"
check_sha256sum "libffi_${LIBFFI_VERSION}.orig.tar.gz" ${LIBFFI_SHA256}
tar zxf libffi*.orig.tar.gz
PATH=/opt/perl/bin:$PATH
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
