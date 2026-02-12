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
for lib in "${ARM64_DIR}"/lib/*.a; do
    libname=$(basename ${lib})
    if [ -f "${X86_64_DIR}/lib/${libname}" ]; then
        echo "Merging ${libname}"
        lipo -create ${ARM64_DIR}/lib/${libname} ${X86_64_DIR}/lib/${libname} \
            -output ${MACOS_OUTPUT}/lib/${libname}
    fi
done

echo "Done. Universal2 artifacts in ${MACOS_OUTPUT}/"
file ${MACOS_OUTPUT}/lib/*.a
