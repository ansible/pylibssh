#!/bin/bash
# Update system packages

# Stop at any error, show all commands
set -exuo pipefail

if [ $(uname -m) = "x86_64" ]; then
  if stat /etc/redhat-release 1>&2 2>/dev/null; then
    yum -y install prelink
    yum -y clean all
    rm -rf /var/cache/yum
  else
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq
    apt-get install -qq -y --no-install-recommends prelink
    apt-get clean -qq
    rm -rf /var/lib/apt/lists/*
  fi
fi
