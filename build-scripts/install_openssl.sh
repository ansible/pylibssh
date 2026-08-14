#!/bin/bash
set -eEuo pipefail

# Shared OpenSSL installation script for both macOS and Linux
# Usage: install_openssl.sh <install_prefix> [platform] [arch]
#   install_prefix: Where to install OpenSSL (required)
#   platform: macos or linux (auto-detected if not provided)
#   arch: Architecture for macOS cross-compilation (optional, default: native)

# Parse arguments
INSTALL_PREFIX="${1:?Install prefix required}"
PLATFORM="${2:-$(uname -s | tr '[:upper:]' '[:lower:]')}"
ARCH="${3:-$(uname -m)}"

# Normalize platform name
case "$PLATFORM" in
    darwin*|macos|osx)
        PLATFORM="macos"
        ;;
    linux*)
        PLATFORM="linux"
        ;;
    *)
        echo "Error: Unsupported platform: $PLATFORM" >&2
        exit 1
        ;;
esac

# Get script directory to source version file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Try to source platform-specific version file, fall back to manylinux version
if [ "$PLATFORM" = "macos" ] && [ -f "${SCRIPT_DIR}/macos/config.sh" ]; then
    source "${SCRIPT_DIR}/macos/config.sh"
elif [ -f "${SCRIPT_DIR}/manylinux-container-image/openssl-version.sh" ]; then
    source "${SCRIPT_DIR}/manylinux-container-image/openssl-version.sh"
else
    echo "Error: Could not find OpenSSL version configuration" >&2
    exit 1
fi

# Strip "openssl-" prefix if present
OPENSSL_VERSION="${OPENSSL_VERSION#openssl-}"

echo "Installing OpenSSL ${OPENSSL_VERSION} for ${PLATFORM} (${ARCH}) to ${INSTALL_PREFIX}"

# Download OpenSSL from GitHub (try GitHub first, fall back to openssl.org)
OPENSSL_URL="https://github.com/openssl/openssl/releases/download/openssl-${OPENSSL_VERSION}/openssl-${OPENSSL_VERSION}.tar.gz"
OPENSSL_TARBALL="openssl-${OPENSSL_VERSION}.tar.gz"

echo "Downloading OpenSSL from GitHub..."
if ! curl -fsSL "${OPENSSL_URL}" -o "${OPENSSL_TARBALL}"; then
    echo "GitHub download failed, trying openssl.org..."
    OPENSSL_URL="https://www.openssl.org/source/openssl-${OPENSSL_VERSION}.tar.gz"
    curl -fsSL "${OPENSSL_URL}" -o "${OPENSSL_TARBALL}"
fi

# Verify SHA256 checksum if available
if [ -n "${OPENSSL_SHA256:-}" ]; then
    echo "Verifying SHA256 checksum..."
    if command -v sha256sum &> /dev/null; then
        echo "${OPENSSL_SHA256}  ${OPENSSL_TARBALL}" | sha256sum -c -
    elif command -v shasum &> /dev/null; then
        echo "${OPENSSL_SHA256}  ${OPENSSL_TARBALL}" | shasum -a 256 -c -
    else
        echo "Warning: No SHA256 verification tool found, skipping checksum" >&2
    fi
else
    echo "Warning: No SHA256 checksum provided, skipping verification" >&2
fi

# Extract tarball
echo "Extracting OpenSSL..."
tar xzf "${OPENSSL_TARBALL}"
cd "openssl-${OPENSSL_VERSION}"

# Platform-specific configuration
if [ "$PLATFORM" = "macos" ]; then
    # macOS-specific configuration

    # Normalize architecture for OpenSSL target
    CMAKE_ARCH="${ARCH}"
    if [ "${ARCH}" = "x86" ] || [ "${ARCH}" = "x86_64" ]; then
        CMAKE_ARCH="x86_64"
    fi

    # Set macOS deployment target
    export MACOSX_DEPLOYMENT_TARGET="${MACOSX_DEPLOYMENT_TARGET:-11.0}"

    # Set CFLAGS for cross-compilation
    if [ "${ARCH}" = "arm64" ]; then
        export CFLAGS="${CFLAGS:-} -mmacosx-version-min=${MACOSX_DEPLOYMENT_TARGET}"
    else
        export CFLAGS="${CFLAGS:-} -mmacosx-version-min=${MACOSX_DEPLOYMENT_TARGET} -march=core2"
    fi

    OPENSSL_TARGET="darwin64-${CMAKE_ARCH}-cc"
    CONFIG_FLAGS="--prefix=${INSTALL_PREFIX} no-shared no-tests"

    echo "Configuring OpenSSL for macOS (${CMAKE_ARCH})..."
    ./Configure ${OPENSSL_TARGET} ${CONFIG_FLAGS}

    # Build using all available cores
    NPROC=$(sysctl -n hw.ncpu 2>/dev/null || echo 4)

elif [ "$PLATFORM" = "linux" ]; then
    # Linux-specific configuration

    # Determine build flags based on architecture
    BUILD_FLAGS="${OPENSSL_BUILD_FLAGS:-no-shared no-tests}"

    # Check for specific architectures
    if [ -x /proc/self/exe ]; then
        if readelf -h /proc/self/exe 2>/dev/null | grep -q 'Machine:.* ARM'; then
            BUILD_FLAGS="${OPENSSL_BUILD_FLAGS_ARMV7L:-linux-armv4 ${BUILD_FLAGS}}"
        elif readelf -h /proc/self/exe 2>/dev/null | grep -q 'Machine:.* S/390'; then
            BUILD_FLAGS="${OPENSSL_BUILD_FLAGS_S390X:-${BUILD_FLAGS}}"
            export CFLAGS="${CFLAGS:-} -march=z10"
        fi
    fi

    echo "Configuring OpenSSL for Linux..."
    ./config ${BUILD_FLAGS} --prefix=${INSTALL_PREFIX} --openssldir=${INSTALL_PREFIX}

    # For older OpenSSL versions that need make depend
    if grep -q "^depend:" Makefile 2>/dev/null; then
        make depend
    fi

    # Build using all available cores
    NPROC=$(nproc 2>/dev/null || echo 4)
fi

echo "Building OpenSSL..."
make -j${NPROC}

echo "Installing OpenSSL to ${INSTALL_PREFIX}..."
# Install only software and SSL directories (skip docs)
make install_sw install_ssldirs

echo "OpenSSL ${OPENSSL_VERSION} installed successfully to ${INSTALL_PREFIX}"
