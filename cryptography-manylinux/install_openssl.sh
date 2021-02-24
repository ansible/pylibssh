#!/bin/bash
set -xe

unset RELEASE

OPENSSL_URL="https://www.openssl.org/source/"
source /root/openssl-version.sh

function check_sha256sum {
    local fname=$1
    local sha256=$2
    echo "${sha256}  ${fname}" > "${fname}.sha256"
    sha256sum -c "${fname}.sha256"
    rm "${fname}.sha256"
}

curl -#O "${OPENSSL_URL}/${OPENSSL_VERSION}.tar.gz"
check_sha256sum ${OPENSSL_VERSION}.tar.gz ${OPENSSL_SHA256}
tar zxf ${OPENSSL_VERSION}.tar.gz
PATH=/opt/perl/bin:$PATH
pushd ${OPENSSL_VERSION}
./config $OPENSSL_BUILD_FLAGS --prefix=/opt/pyca/cryptography/openssl --openssldir=/opt/pyca/cryptography/openssl
make depend
make -j4
# avoid installing the docs
# https://github.com/openssl/openssl/issues/6685#issuecomment-403838728
make install_sw install_ssldirs
popd
rm -rf openssl*
