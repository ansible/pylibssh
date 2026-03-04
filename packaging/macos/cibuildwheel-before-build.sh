#!/bin/bash

set -eEuo pipefail

# Get repository root and script directory
REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source macOS build configuration
source "${SCRIPT_DIR}/config.sh"

# Determine target architecture from cibuildwheel environment
# ARCHFLAGS is set by cibuildwheel for macOS builds
# Example: "-arch arm64" or "-arch x86_64" or "-arch arm64 -arch x86_64"
if [[ "${ARCHFLAGS:-}" == *"arm64"* ]] && [[ "${ARCHFLAGS:-}" == *"x86_64"* ]]; then
    # Building universal2 wheel
    BUILD_MODE="universal2"
    echo "Building universal2 wheel with libssh ${LIBSSH_VERSION}"
elif [[ "${ARCHFLAGS:-}" == *"arm64"* ]]; then
    # Building arm64-only wheel
    BUILD_MODE="arm64"
    echo "Building arm64 wheel with libssh ${LIBSSH_VERSION}"
elif [[ "${ARCHFLAGS:-}" == *"x86_64"* ]]; then
    # Building x86_64-only wheel
    BUILD_MODE="x86_64"
    echo "Building x86_64 wheel with libssh ${LIBSSH_VERSION}"
else
    # Fallback: detect host architecture
    HOST_ARCH="$(uname -m)"
    if [ "${HOST_ARCH}" = "arm64" ]; then
        BUILD_MODE="arm64"
    else
        BUILD_MODE="x86_64"
    fi
    echo "No ARCHFLAGS set, building for host architecture: ${BUILD_MODE} with libssh ${LIBSSH_VERSION}"
fi

# Use MACOS_OUTPUT from environment (set in pyproject.toml)
MACOS_OUTPUT="${MACOS_OUTPUT:-packaging/macos/build}"
MACOS_OUTPUT_ABS="${REPO_ROOT}/${MACOS_OUTPUT}"

# Build libssh for required architecture(s)
if [ "${BUILD_MODE}" = "universal2" ]; then
    # Build for both architectures
    echo "Building libssh for arm64..."
    bash "${SCRIPT_DIR}/build-libssh-macos.sh" "${LIBSSH_VERSION}" "arm64"

    echo "Building libssh for x86_64..."
    bash "${SCRIPT_DIR}/build-libssh-macos.sh" "${LIBSSH_VERSION}" "x86"

    # Merge into universal2
    echo "Merging into universal2..."
    bash "${SCRIPT_DIR}/merge-universal2.sh" \
        "${MACOS_OUTPUT_ABS}/arm64" \
        "${MACOS_OUTPUT_ABS}/x86_64" \
        "${MACOS_OUTPUT_ABS}/universal2"

    # Export paths for universal2 build
    STATIC_DEPS_PATH="${MACOS_OUTPUT_ABS}/universal2"
elif [ "${BUILD_MODE}" = "x86_64" ]; then
    # Build for x86_64 only (normalize to x86 for the script)
    bash "${SCRIPT_DIR}/build-libssh-macos.sh" "${LIBSSH_VERSION}" "x86"
    STATIC_DEPS_PATH="${MACOS_OUTPUT_ABS}/x86_64"
else
    # Build for arm64 only
    bash "${SCRIPT_DIR}/build-libssh-macos.sh" "${LIBSSH_VERSION}" "arm64"
    STATIC_DEPS_PATH="${MACOS_OUTPUT_ABS}/arm64"
fi

# Export environment variables for the build
# These will be used by the Python extension build
export CFLAGS="-I${STATIC_DEPS_PATH}/include ${CFLAGS:-}"
export LDFLAGS="-L${STATIC_DEPS_PATH}/lib ${LDFLAGS:-}"
export PKG_CONFIG_PATH="${STATIC_DEPS_PATH}/lib/pkgconfig:${PKG_CONFIG_PATH:-}"

# Verify the libraries were built correctly
echo "Verifying built libraries in ${STATIC_DEPS_PATH}..."
ls -lh "${STATIC_DEPS_PATH}/lib/"*.a || true
file "${STATIC_DEPS_PATH}/lib/libssh.a" || true

echo "Static dependencies path: ${STATIC_DEPS_PATH}"
echo "CFLAGS: ${CFLAGS}"
echo "LDFLAGS: ${LDFLAGS}"
echo "Build preparation complete."
