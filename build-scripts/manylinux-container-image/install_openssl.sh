#!/bin/bash
set -xe

unset RELEASE

# Get script directory
MY_DIR=$(dirname "${BASH_SOURCE[0]}")

# Get build utilities
source $MY_DIR/build_utils.sh

OPENSSL_URL="https://github.com/openssl/openssl/releases/download"
source /root/openssl-version.sh

curl -#LO "${OPENSSL_URL}/${OPENSSL_VERSION}/${OPENSSL_VERSION}.tar.gz"
check_sha256sum "${OPENSSL_VERSION}.tar.gz" ${OPENSSL_SHA256}
tar zxf ${OPENSSL_VERSION}.tar.gz

pushd ${OPENSSL_VERSION}
BUILD_FLAGS="$OPENSSL_BUILD_FLAGS"
if [[ "$1" =~ '^manylinux1_.*$' ]]; then
  PATH=/opt/perl/bin:$PATH
fi
# Can't use `$(uname -m) = "armv7l"` because that returns what kernel we're
# using, and we build for armv7l with an ARM64 host.
if [ "$(readelf -h /proc/self/exe | grep -o 'Machine:.* ARM')" ]; then
    BUILD_FLAGS="$OPENSSL_BUILD_FLAGS_ARMV7L"
fi
if [ "$(readelf -h /proc/self/exe | grep -o 'Machine:.* S/390')" ]; then
    BUILD_FLAGS="$OPENSSL_BUILD_FLAGS_S390X"
    export CFLAGS="$CFLAGS -march=z10"
fi
./config $BUILD_FLAGS --prefix=/opt/pyca/cryptography/openssl --openssldir=/opt/pyca/cryptography/openssl
make depend
make -j4
# avoid installing the docs
# https://github.com/openssl/openssl/issues/6685#issuecomment-403838728
make install_sw install_ssldirs
popd
rm -rf openssl*
