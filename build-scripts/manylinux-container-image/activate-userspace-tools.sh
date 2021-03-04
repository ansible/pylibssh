#!/bin/bash
set -xe

USERSPACE_LOCAL_BIN_PATH="${HOME}/.local/bin"
USERSPACE_VENV_PATH="${HOME}/.tools-venv"
USERSPACE_VENV_BIN_PATH="${USERSPACE_VENV_PATH}/bin"

PATH="${USERSPACE_VENV_BIN_PATH}:${USERSPACE_LOCAL_BIN_PATH}:${PATH}"

function import_userspace_tools {
    export USERSPACE_VENV_PATH
    export USERSPACE_VENV_BIN_PATH
    export PATH
}

export import_userspace_tools
