#!/bin/bash

set -eEuo pipefail

# Prompt for build parameters
read -p "libssh version [0.10.6]: " LIBSSH_VERSION
LIBSSH_VERSION=${LIBSSH_VERSION:-0.10.6}

read -p "OpenSSL version [3.0.13]: " OPENSSL_VERSION
OPENSSL_VERSION=${OPENSSL_VERSION:-3.0.13}

read -p "Architecture (arm64/x86_64) [$(uname -m)]: " ARCH
ARCH=${ARCH:-$(uname -m)}

OUTPUT_DIR="artifacts/${ARCH}"
mkdir -p ${OUTPUT_DIR}

WORK_DIR=$(mktemp -d)
cd ${WORK_DIR}

echo "Building in ${WORK_DIR}"
echo "libssh: ${LIBSSH_VERSION}, OpenSSL: ${OPENSSL_VERSION}, Arch: ${ARCH}"

export MACOSX_DEPLOYMENT_TARGET="10.13"

# Build OpenSSL
echo "Downloading OpenSSL..."
curl -sL https://www.openssl.org/source/openssl-${OPENSSL_VERSION}.tar.gz | tar xz
cd openssl-${OPENSSL_VERSION}

if [ "${ARCH}" = "arm64" ]; then
    OPENSSL_TARGET="darwin64-arm64-cc"
else
    OPENSSL_TARGET="darwin64-x86_64-cc"
fi

./Configure ${OPENSSL_TARGET} --prefix=${WORK_DIR}/deps no-shared no-tests
make -j$(sysctl -n hw.ncpu) > /dev/null
make install_sw > /dev/null
cd ..

# Build libssh
echo "Downloading libssh..."
curl -sL https://www.libssh.org/files/$(echo ${LIBSSH_VERSION} | cut -d. -f1-2)/libssh-${LIBSSH_VERSION}.tar.xz | tar xJ
cd libssh-${LIBSSH_VERSION}
mkdir build && cd build

cmake .. \
    -DCMAKE_INSTALL_PREFIX=${WORK_DIR}/deps \
    -DCMAKE_OSX_ARCHITECTURES=${ARCH} \
    -DCMAKE_OSX_DEPLOYMENT_TARGET=${MACOSX_DEPLOYMENT_TARGET} \
    -DOPENSSL_ROOT_DIR=${WORK_DIR}/deps \
    -DBUILD_SHARED_LIBS=OFF \
    -DWITH_EXAMPLES=OFF \
    -DWITH_SERVER=OFF \
    -DUNIT_TESTING=OFF \
    > /dev/null

make -j$(sysctl -n hw.ncpu) > /dev/null
make install > /dev/null

# Package artifacts
cd ${WORK_DIR}/deps
ARTIFACT_NAME="libssh-${LIBSSH_VERSION}-openssl-${OPENSSL_VERSION}-macos-${ARCH}"
mkdir -p ${ARTIFACT_NAME}/{lib,include}

cp lib/*.a ${ARTIFACT_NAME}/lib/
cp -r include/* ${ARTIFACT_NAME}/include/

tar czf ${ARTIFACT_NAME}.tar.gz ${ARTIFACT_NAME}
shasum -a 256 ${ARTIFACT_NAME}.tar.gz > ${ARTIFACT_NAME}.tar.gz.sha256

# Move to output directory
mv ${ARTIFACT_NAME}.tar.gz* ${OLDPWD}/${OUTPUT_DIR}/

cd ${OLDPWD}
rm -rf ${WORK_DIR}

echo "Done. Artifacts in ${OUTPUT_DIR}/"
ls -lh ${OUTPUT_DIR}/
