#!/bin/bash
set -xe

STATIC_DEPS_DIR_STORAGE=.static-deps-path
STATIC_DEPS_DIR="$(mktemp -d '/opt/manylinux-static-deps.XXXXXXXXXX')"

mkdir -pv "${STATIC_DEPS_DIR}"
echo "${STATIC_DEPS_DIR}" > "${STATIC_DEPS_DIR_STORAGE}"

>&2 echo
>&2 echo
>&2 echo ==================================================================================================
>&2 echo Created static deps path "'${STATIC_DEPS_DIR}'" and stored it to "'${STATIC_DEPS_DIR_STORAGE}'"...
>&2 echo ==================================================================================================
>&2 echo
