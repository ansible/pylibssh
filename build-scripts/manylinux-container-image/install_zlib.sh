#!/bin/bash
set -xe

unset RELEASE

# Get script directory
MY_DIR=$(dirname "${BASH_SOURCE[0]}")

# Get build utilities
source $MY_DIR/build_utils.sh
source get-static-deps-dir.sh

ZLIB_SHA256="b3a24de97a8fdbc835b9833169501030b8977031bcb54b3b3ac13740f846ab30"
ZLIB_VERSION="1.2.13"

fetch_source "zlib-${ZLIB_VERSION}.tar.gz" "https://github.com/madler/zlib/releases/download/v${ZLIB_VERSION}"
check_sha256sum "zlib-${ZLIB_VERSION}.tar.gz" ${ZLIB_SHA256}
tar zxf "zlib-${ZLIB_VERSION}.tar.gz"

pushd "zlib-${ZLIB_VERSION}"
export CFLAGS="-fPIC"
STATIC_DEPS_PREFIX="$(get_static_deps_dir)"
./configure --static --prefix="${STATIC_DEPS_PREFIX}"
make -j libz.a
make install
popd
rm -rf "zlib-${ZLIB_VERSION}"
