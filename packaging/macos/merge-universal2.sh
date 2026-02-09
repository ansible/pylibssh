#!/bin/bash

set -eEuo pipefail

if [ $# -ne 3 ]; then
    echo "Usage: $0 <arm64_dir> <x86_64_dir> <output_dir>"
    exit 1
fi

ARM64_DIR=$1
X86_64_DIR=$2
OUTPUT_DIR=$3

if [ ! -d "${ARM64_DIR}" ] || [ ! -d "${X86_64_DIR}" ]; then
    echo "Error: Input directories don't exist"
    exit 1
fi

mkdir -p ${OUTPUT_DIR}/{lib,include}

echo "Merging ${ARM64_DIR} and ${X86_64_DIR} into ${OUTPUT_DIR}"

# Copy headers from arm64 (should be identical)
cp -r ${ARM64_DIR}/include/* ${OUTPUT_DIR}/include/

# Merge libraries using lipo
for lib in ${ARM64_DIR}/lib/*.a; do
    libname=$(basename ${lib})
    if [ -f "${X86_64_DIR}/lib/${libname}" ]; then
        echo "Merging ${libname}"
        lipo -create ${ARM64_DIR}/lib/${libname} ${X86_64_DIR}/lib/${libname} \
            -output ${OUTPUT_DIR}/lib/${libname}
    fi
done

echo "Done. Universal2 artifacts in ${OUTPUT_DIR}/"
file ${OUTPUT_DIR}/lib/*.a | head -3
