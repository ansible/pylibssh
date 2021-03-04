#!/bin/bash
set -xe

STATIC_DEPS_DIR_STORAGE=.static-deps-path
STATIC_DEPS_DIR=$(cat "${STATIC_DEPS_DIR_STORAGE}")

function get_static_deps_dir {
    echo "${STATIC_DEPS_DIR}"
}

export get_static_deps_dir
