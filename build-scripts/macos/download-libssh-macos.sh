#!/bin/bash

set -eEuo pipefail

# Download pre-built libssh artifacts for macOS
# This avoids expensive rebuilds on every CI run

# Get repository root
REPO_ROOT="$(git rev-parse --show-toplevel)"

# Source versions from macOS-specific config
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/config.sh"

# Strip "openssl-" prefix from OPENSSL_VERSION if present
OPENSSL_VERSION="${OPENSSL_VERSION#openssl-}"

# Parse CLI arguments (or use defaults from config.sh)
LIBSSH_VERSION="${1:-${LIBSSH_VERSION}}"
ARCH="${2}"

# Use MACOS_OUTPUT environment variable from pyproject.toml [tool.cibuildwheel.macos.environment]
# Default to build-scripts/macos/build if not set
MACOS_OUTPUT="${MACOS_OUTPUT:-build-scripts/macos/build}"
MACOS_OUTPUT="${REPO_ROOT}/${MACOS_OUTPUT}/${ARCH}"
mkdir -p ${MACOS_OUTPUT}
MACOS_OUTPUT_ABS="$(cd ${MACOS_OUTPUT} && pwd)"

# Artifact naming convention (must match build-libssh-macos.sh)
ARTIFACT_NAME="libssh-${LIBSSH_VERSION}-openssl-${OPENSSL_VERSION}-macos-${ARCH}"
TARBALL_NAME="${ARTIFACT_NAME}.tar.gz"
SHA256_NAME="${TARBALL_NAME}.sha256"

# GitHub release URL
# TODO: Update with actual release tag pattern
# For now, we'll use a tag like: libssh-v${LIBSSH_VERSION}-openssl-${OPENSSL_VERSION}
RELEASE_TAG="libssh-v${LIBSSH_VERSION}-openssl-${OPENSSL_VERSION}"
GITHUB_REPO="ansible/pylibssh"
DOWNLOAD_URL="https://github.com/${GITHUB_REPO}/releases/download/${RELEASE_TAG}/${TARBALL_NAME}"
SHA256_URL="https://github.com/${GITHUB_REPO}/releases/download/${RELEASE_TAG}/${SHA256_NAME}"

echo "Attempting to download pre-built libssh for macOS ${ARCH}..."
echo "  libssh: ${LIBSSH_VERSION}"
echo "  OpenSSL: ${OPENSSL_VERSION}"
echo "  URL: ${DOWNLOAD_URL}"

WORK_DIR=$(mktemp -d)
cd ${WORK_DIR}

# Try to download tarball
if ! curl -fsSL "${DOWNLOAD_URL}" -o "${TARBALL_NAME}"; then
    echo "Failed to download pre-built artifact from ${DOWNLOAD_URL}"
    rm -rf ${WORK_DIR}
    exit 1
fi

# Try to download SHA256 checksum
if ! curl -fsSL "${SHA256_URL}" -o "${SHA256_NAME}"; then
    echo "Warning: SHA256 file not found, skipping verification"
else
    # Verify checksum
    echo "Verifying SHA256 checksum..."
    if command -v sha256sum &> /dev/null; then
        sha256sum -c "${SHA256_NAME}"
    elif command -v shasum &> /dev/null; then
        shasum -a 256 -c "${SHA256_NAME}"
    else
        echo "Warning: No SHA256 verification tool found, skipping checksum"
    fi
fi

# Extract tarball
echo "Extracting ${TARBALL_NAME}..."
tar xzf "${TARBALL_NAME}"

# Copy extracted files to output directory
echo "Installing to ${MACOS_OUTPUT_ABS}..."
mkdir -p ${MACOS_OUTPUT_ABS}/lib ${MACOS_OUTPUT_ABS}/include

cp -r ${ARTIFACT_NAME}/lib/*.a ${MACOS_OUTPUT_ABS}/lib/
cp -r ${ARTIFACT_NAME}/include/* ${MACOS_OUTPUT_ABS}/include/

# Copy pkgconfig if it exists
if [ -d ${ARTIFACT_NAME}/lib/pkgconfig ]; then
    mkdir -p ${MACOS_OUTPUT_ABS}/lib/pkgconfig
    cp -r ${ARTIFACT_NAME}/lib/pkgconfig/* ${MACOS_OUTPUT_ABS}/lib/pkgconfig/
fi

# Also save the tarball to output directory for reference
cp "${TARBALL_NAME}" "${SHA256_NAME}" ${MACOS_OUTPUT_ABS}/

# Cleanup
cd ${OLDPWD}
rm -rf ${WORK_DIR}

echo "Successfully downloaded and installed pre-built libssh to ${MACOS_OUTPUT_ABS}"
ls -lh ${MACOS_OUTPUT_ABS}/lib/*.a
