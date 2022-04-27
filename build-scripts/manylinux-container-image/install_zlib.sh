#!/bin/bash
set -xe

unset RELEASE

# Get script directory
MY_DIR=$(dirname "${BASH_SOURCE[0]}")

# Get build utilities
source $MY_DIR/build_utils.sh
source get-static-deps-dir.sh

ZLIB_SHA256="91844808532e5ce316b3c010929493c0244f3d37593afd6de04f71821d5136d9"
ZLIB_VERSION="1.2.12"

fetch_source "zlib-${ZLIB_VERSION}.tar.gz" "https://www.zlib.net"
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
