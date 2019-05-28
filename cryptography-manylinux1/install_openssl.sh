#!/bin/bash
set -xe

OPENSSL_URL="https://www.openssl.org/source/"
OPENSSL_NAME="openssl-1.1.1c"
OPENSSL_SHA256="f6fb3079ad15076154eda9413fed42877d668e7069d9b87396d0804fdb3f4c90"

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
echo "Configuring for x86_64"
./config no-comp enable-ec_nistp_64_gcc_128 no-shared no-dynamic-engine --prefix=/opt/pyca/cryptography/openssl --openssldir=/opt/pyca/cryptography/openssl
make depend
make -j4
# avoid installing the docs
# https://github.com/openssl/openssl/issues/6685#issuecomment-403838728
make install_sw install_ssldirs
