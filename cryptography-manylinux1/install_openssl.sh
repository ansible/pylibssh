#!/bin/bash
set -xe

OPENSSL_URL="https://www.openssl.org/source/"
OPENSSL_NAME="openssl-1.1.0j"
OPENSSL_SHA256="31bec6c203ce1a8e93d5994f4ed304c63ccf07676118b6634edded12ad1b3246"

function check_sha256sum {
    local fname=$1
    local sha256=$2
    echo "${sha256}  ${fname}" > "${fname}.sha256"
    sha256sum -c "${fname}.sha256"
    rm "${fname}.sha256"
}

curl -#O "${OPENSSL_URL}/${OPENSSL_NAME}.tar.gz"
check_sha256sum ${OPENSSL_NAME}.tar.gz ${OPENSSL_SHA256}
tar zxf ${OPENSSL_NAME}.tar.gz
PATH=/opt/perl/bin:$PATH
cd ${OPENSSL_NAME}
if [[ $1 == "x86_64" ]]; then
    echo "Configuring for x86_64"
    ./config no-comp enable-ec_nistp_64_gcc_128 no-shared no-dynamic-engine --prefix=/opt/pyca/cryptography/openssl --openssldir=/opt/pyca/cryptography/openssl
else
    echo "Configuring for i686"
    linux32 ./config no-comp no-shared no-dynamic-engine --prefix=/opt/pyca/cryptography/openssl --openssldir=/opt/pyca/cryptography/openssl
fi
make depend
make -j4
# avoid installing the docs
# https://github.com/openssl/openssl/issues/6685#issuecomment-403838728
make install_sw install_ssldirs
