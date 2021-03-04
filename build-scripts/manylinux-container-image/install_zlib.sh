#!/bin/bash
set -xe

unset RELEASE

source get-static-deps-dir.sh

LIB_NAME=zlib
BUILD_DIR=$(mktemp -d "/tmp/${LIB_NAME}-manylinux-build.XXXXXXXXXX")

LIB_VERSION=1.2.11
LIB_DOWNLOAD_DIR="${BUILD_DIR}/${LIB_NAME}-${LIB_VERSION}"

STATIC_DEPS_PREFIX="$(get_static_deps_dir)"

export CFLAGS="-fPIC"

>&2 echo
>&2 echo
>&2 echo ============================================
>&2 echo downloading source of ${LIB_NAME} v${LIB_VERSION}:
>&2 echo ============================================
>&2 echo
curl https://www.zlib.net/${LIB_NAME}-${LIB_VERSION}.tar.gz | \
    tar xzvC "${BUILD_DIR}" -f -

pushd "${LIB_DOWNLOAD_DIR}"
./configure \
    --static \
    --prefix="${STATIC_DEPS_PREFIX}" && \
    make -j libz.a && \
    make install
popd

rm -rf "${BUILD_DIR}"
