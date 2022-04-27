#!/bin/bash
# Helper utilities for build borrowed from https://github.com/pypa/manylinux/blob/main/docker/build_scripts/build_utils.sh


function check_var {
    if [ -z "$1" ]; then
        echo "required variable not defined"
        exit 1
    fi
}


function fetch_source {
    # This is called both inside and outside the build context (e.g. in Travis) to prefetch
    # source tarballs, where curl exists (and works)
    local file=$1
    check_var ${file}
    local url=$2
    check_var ${url}
    if [ $(uname -m) = "s390x" ] || [ $(uname -m) = "ppc64le" ]; then
        # Expired certificate issue on these platforms
        # https://github.com/pypa/manylinux/issues/1203
        unset SSL_CERT_FILE
    fi
    if [ -f ${file} ]; then
        echo "${file} exists, skipping fetch"
    else
        curl -fsSL -o ${file} ${url}/${file}
    fi
}


function check_sha256sum {
    local fname=$1
    check_var ${fname}
    local sha256=$2
    check_var ${sha256}
    echo "${sha256}  ${fname}" > "${fname}.sha256"
    sha256sum -c "${fname}.sha256"
    rm "${fname}.sha256"
}
