#!/bin/bash
set -xe

unset RELEASE

# Get script directory
MY_DIR=$(dirname "${BASH_SOURCE[0]}")

# Get build utilities
source $MY_DIR/build_utils.sh

OPENSSL_URL="https://www.openssl.org/source/"
source /root/openssl-version.sh

fetch_source ${OPENSSL_VERSION}.tar.gz ${OPENSSL_URL}
check_sha256sum "${OPENSSL_VERSION}.tar.gz" ${OPENSSL_SHA256}
tar zxf ${OPENSSL_VERSION}.tar.gz
pushd ${OPENSSL_VERSION}
if [[ "$1" =~ '^manylinux1_.*$' ]]; then
  PATH=/opt/perl/bin:$PATH
fi
./config $OPENSSL_BUILD_FLAGS --prefix=/opt/pyca/cryptography/openssl --openssldir=/opt/pyca/cryptography/openssl
make depend
make -j4
# avoid installing the docs
# https://github.com/openssl/openssl/issues/6685#issuecomment-403838728
make install_sw install_ssldirs
popd
rm -rf openssl*
