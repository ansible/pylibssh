#!/bin/bash

set -eEuo pipefail

# Get repository root (works in CI and local dev)
REPO_ROOT="$(git rev-parse --show-toplevel)"

# Source versions from macOS-specific config
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/config.sh"

# Strip "openssl-" prefix from OPENSSL_VERSION if present
OPENSSL_VERSION="${OPENSSL_VERSION#openssl-}"

# Parse CLI arguments (or use defaults from config.sh)
LIBSSH_VERSION="${1:-${LIBSSH_VERSION}}"
ARCH="${2}"

# Normalize architecture for CMake (x86 -> x86_64)
CMAKE_ARCH="${ARCH}"
if [ "${ARCH}" = "x86" ]; then
    CMAKE_ARCH="x86_64"
fi

# Use MACOS_OUTPUT environment variable from pyproject.toml [tool.cibuildwheel.macos.environment]
# Default to packaging/macos/build if not set
MACOS_OUTPUT="${MACOS_OUTPUT:-packaging/macos/build}"
MACOS_OUTPUT="${REPO_ROOT}/${MACOS_OUTPUT}/${ARCH}"
mkdir -p ${MACOS_OUTPUT}
MACOS_OUTPUT_ABS="$(cd ${MACOS_OUTPUT} && pwd)"
# Store absolute path for use in environment variables (similar to /root/.static-deps-path)
echo "${MACOS_OUTPUT_ABS}" > "${REPO_ROOT}/.macos-static-deps-path-${ARCH}"

WORK_DIR=$(mktemp -d)
cd ${WORK_DIR}

echo "Building in ${WORK_DIR}"
echo "libssh: ${LIBSSH_VERSION}, OpenSSL: ${OPENSSL_VERSION}, Arch: ${ARCH}"

export MACOSX_DEPLOYMENT_TARGET="11.0"

# Set CFLAGS for cross-compilation and deployment target
if [ "${ARCH}" = "arm64" ]; then
    export CFLAGS="-mmacosx-version-min=11.0"
else
    export CFLAGS="-mmacosx-version-min=11.0 -march=core2"
fi

# Build OpenSSL
echo "Downloading OpenSSL..."
curl -sL https://www.openssl.org/source/openssl-${OPENSSL_VERSION}.tar.gz | tar xz
cd openssl-${OPENSSL_VERSION}

OPENSSL_TARGET="darwin64-${ARCH}-cc"

./Configure ${OPENSSL_TARGET} --prefix=${WORK_DIR}/deps no-shared no-tests
make -j$(sysctl -n hw.ncpu) > /dev/null
make install_sw > /dev/null
cd ..

# Build libssh
echo "Downloading libssh..."
curl -sL https://www.libssh.org/files/$(echo ${LIBSSH_VERSION} | cut -d. -f1-2)/libssh-${LIBSSH_VERSION}.tar.xz | tar xJ
cd libssh-${LIBSSH_VERSION}

# Patch CMakeLists.txt to update minimum required CMake version
sed -i '' 's/cmake_minimum_required(VERSION [0-9.]*)/cmake_minimum_required(VERSION 3.5)/' CMakeLists.txt

mkdir build && pushd build

cmake .. \
    -DCMAKE_INSTALL_PREFIX=${WORK_DIR}/deps \
    -DCMAKE_OSX_ARCHITECTURES=${CMAKE_ARCH} \
    -DCMAKE_OSX_DEPLOYMENT_TARGET=${MACOSX_DEPLOYMENT_TARGET} \
    -DOPENSSL_ROOT_DIR=${WORK_DIR}/deps \
    -DBUILD_SHARED_LIBS=OFF \
    -DWITH_EXAMPLES=OFF \
    -DWITH_SERVER=OFF \
    -DUNIT_TESTING=OFF \

make -j$(sysctl -n hw.ncpu) > /dev/null
make install > /dev/null

# Package artifacts
popd
cd ${WORK_DIR}/deps
ARTIFACT_NAME="libssh-${LIBSSH_VERSION}-openssl-${OPENSSL_VERSION}-macos-${ARCH}"
mkdir -pv ${ARTIFACT_NAME}/{lib,include}

cp lib/*.a ${ARTIFACT_NAME}/lib/
cp -r include/* ${ARTIFACT_NAME}/include/

tar czf ${ARTIFACT_NAME}.tar.gz ${ARTIFACT_NAME}
shasum -a 256 ${ARTIFACT_NAME}.tar.gz > ${ARTIFACT_NAME}.tar.gz.sha256

# Move to output directory (use absolute path)
mv ${ARTIFACT_NAME}.tar.gz* ${MACOS_OUTPUT_ABS}/

cd ${OLDPWD}
rm -rf ${WORK_DIR}

echo "Done. Artifacts in ${MACOS_OUTPUT_ABS}/"
ls -lh ${MACOS_OUTPUT_ABS}/
