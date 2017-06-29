#!/bin/bash
set -xe

OPENSSL_URL="https://www.openssl.org/source/"
OPENSSL_NAME="openssl-1.1.0f"
OPENSSL_SHA256="12f746f3f2493b2f39da7ecf63d7ee19c6ac9ec6a4fcd8c229da8a522cb12765"

function check_sha256sum {
    local fname=$1
    local sha256=$2
    echo "${sha256}  ${fname}" > "${fname}.sha256"
    sha256sum -c "${fname}.sha256"
    rm "${fname}.sha256"
}

curl -#O ${OPENSSL_URL}/${OPENSSL_NAME}.tar.gz
check_sha256sum ${OPENSSL_NAME}.tar.gz ${OPENSSL_SHA256}
tar zxvf ${OPENSSL_NAME}.tar.gz
PATH=/opt/perl/bin:$PATH
cd ${OPENSSL_NAME}
if [[ $1 == "x86_64" ]]; then
    echo "Configuring for x86_64"
    ./Configure linux-x86_64 no-comp enable-ec_nistp_64_gcc_128 shared --prefix=/opt/pyca/cryptography/openssl --openssldir=/opt/pyca/cryptography/openssl
else
    echo "Configuring for i686"
    ./Configure linux-generic32 no-comp shared --prefix=/opt/pyca/cryptography/openssl --openssldir=/opt/pyca/cryptography/openssl
fi
make depend
make -j4
make install
