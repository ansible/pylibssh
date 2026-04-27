#!/bin/bash
set -xe

unset RELEASE

# Get script directory
MY_DIR=$(dirname "${BASH_SOURCE[0]}")

# Get build utilities (for compatibility, though not used anymore)
source $MY_DIR/build_utils.sh

# Source OpenSSL version
source /root/openssl-version.sh

# Handle manylinux1 Perl path
if [[ "$1" =~ '^manylinux1_.*$' ]]; then
  export PATH=/opt/perl/bin:$PATH
fi

# Use shared OpenSSL installer
INSTALL_PREFIX="/opt/pyca/cryptography/openssl"
SHARED_INSTALLER="${MY_DIR}/../install_openssl.sh"

# Create a temporary directory for the build
WORK_DIR=$(mktemp -d)
cd "${WORK_DIR}"

# Run the shared installer
"${SHARED_INSTALLER}" "${INSTALL_PREFIX}" linux

# Clean up
cd /
rm -rf "${WORK_DIR}"
