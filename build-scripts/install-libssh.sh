#!/bin/bash
set -euo pipefail

# Detect architecture
ARCH=$(uname -m)
echo "Building for architecture: $ARCH"

# libssh version to build
LIBSSH_VERSION="0.10.6"

# Check if libssh is already installed with correct version
if pkg-config --exists libssh --atleast-version=0.9.0; then
    echo "libssh already installed with sufficient version"
    pkg-config --modversion libssh
    exit 0
fi

echo "Installing libssh $LIBSSH_VERSION from source..."

# Install build dependencies
if command -v yum >/dev/null 2>&1; then
    yum install -y wget tar cmake make gcc gcc-c++ openssl-devel zlib-devel
elif command -v apt-get >/dev/null 2>&1; then
    apt-get update
    apt-get install -y wget tar cmake make gcc g++ libssl-dev zlib1g-dev
fi

# Download and build libssh
cd /tmp
wget "https://www.libssh.org/files/0.10/libssh-${LIBSSH_VERSION}.tar.xz"
tar -xf "libssh-${LIBSSH_VERSION}.tar.xz"
cd "libssh-${LIBSSH_VERSION}"

mkdir build && cd build
cmake \
    -DCMAKE_INSTALL_PREFIX=/usr/local \
    -DCMAKE_BUILD_TYPE=Release \
    -DWITH_GSSAPI=OFF \
    -DWITH_ZLIB=ON \
    -DWITH_SFTP=ON \
    -DWITH_SERVER=OFF \
    -DWITH_STATIC_LIB=ON \
    -DWITH_EXAMPLES=OFF \
    ..

make -j$(nproc)
make install

# Update library cache
ldconfig || echo "ldconfig not available"

echo "libssh installation completed"
pkg-config --modversion libssh || echo "libssh version check failed"