#!/bin/bash

set -eEuo pipefail

if [ $# -ne 3 ]; then
    echo "Usage: $0 <arm64_dir> <x86_64_dir> <output_dir>"
    exit 1
fi

ARM64_DIR=$1
X86_64_DIR=$2
MACOS_OUTPUT=$3

if [ ! -d "${ARM64_DIR}" ] || [ ! -d "${X86_64_DIR}" ]; then
    echo "Error: Input directories don't exist"
    exit 1
fi

mkdir -pv "${MACOS_OUTPUT}"/lib

echo "Merging ${ARM64_DIR} and ${X86_64_DIR} into ${MACOS_OUTPUT}"

# Copy headers from arm64 (should be identical)
cp -rv "${ARM64_DIR}"/include "${MACOS_OUTPUT}"/

# Copy pkgconfig if it exists
if [ -d "${ARM64_DIR}/lib/pkgconfig" ]; then
    cp -r ${ARM64_DIR}/lib/pkgconfig ${MACOS_OUTPUT}/lib/
fi

# Merge libraries using lipo
# Explicitly list libraries to avoid accidentally picking up unwanted files
echo "Merging libcrypto.a"
lipo -create -output "${MACOS_OUTPUT}/lib/libcrypto.a" \
    "${ARM64_DIR}/lib/libcrypto.a" \
    "${X86_64_DIR}/lib/libcrypto.a"

echo "Merging libssl.a"
lipo -create -output "${MACOS_OUTPUT}/lib/libssl.a" \
    "${ARM64_DIR}/lib/libssl.a" \
    "${X86_64_DIR}/lib/libssl.a"

echo "Merging libssh.a"
lipo -create -output "${MACOS_OUTPUT}/lib/libssh.a" \
    "${ARM64_DIR}/lib/libssh.a" \
    "${X86_64_DIR}/lib/libssh.a"

echo "Done. Universal2 artifacts in ${MACOS_OUTPUT}/"
file ${MACOS_OUTPUT}/lib/*.a
