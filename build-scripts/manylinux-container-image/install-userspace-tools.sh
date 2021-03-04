#!/bin/bash
set -x

set -Eeuo pipefail

source activate-userspace-tools.sh
import_userspace_tools

ARCH=$(uname -m)
PYTHON_INTERPRETER=/opt/python/cp39-cp39/bin/python
VIRTUALENV_PYTHON_BIN="${USERSPACE_VENV_BIN_PATH}/python"
VIRTUALENV_PIP_BIN="${VIRTUALENV_PYTHON_BIN} -m pip"

TOOLS_PKGS=auditwheel
if [ "${ARCH}" == "x86_64" ]
then
    TOOLS_PKGS="${TOOLS_PKGS} cmake"
fi

# Avoid creation of __pycache__/*.py[c|o]
export PYTHONDONTWRITEBYTECODE=1

>&2 echo
>&2 echo
>&2 echo ============================================================================
>&2 echo Installing build deps into a dedicated venv at "'${USERSPACE_VENV_PATH}'"...
>&2 echo ============================================================================
>&2 echo
"${PYTHON_INTERPRETER}" -m venv "${USERSPACE_VENV_PATH}"
${VIRTUALENV_PIP_BIN} install -U pip-with-requires-python
${VIRTUALENV_PIP_BIN} install -U setuptools wheel
${VIRTUALENV_PIP_BIN} install ${TOOLS_PKGS}
