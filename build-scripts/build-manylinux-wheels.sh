#!/usr/bin/env bash

DEBUG=$DEBUG

if [ -n "$DEBUG" ]
then
    set -x
fi

MANYLINUX_TARGET="${1}"
PYTHON_TARGET="${2}"

set -Eeuo pipefail

THIS_SCRIPT_DIR_PATH=$(dirname "$(readlink -m $(type -p "${0}"))")
IMAGE_SCRIPTS_DIR_PATH="${THIS_SCRIPT_DIR_PATH}/manylinux-container-image"

source "${IMAGE_SCRIPTS_DIR_PATH}/get-static-deps-dir.sh"
source "${IMAGE_SCRIPTS_DIR_PATH}/activate-userspace-tools.sh"

SRC_DIR=/io
PERM_REF_HOST_FILE="${SRC_DIR}/setup.cfg"
PEP517_CONFIG_FILE="${SRC_DIR}/pyproject.toml"
DIST_NAME="$(cat "${PERM_REF_HOST_FILE}" | grep '^name = ' | awk '{print$3}' | sed s/-/_/)"
IMPORTABLE_PKG="$(ls "${SRC_DIR}/src/")"  # must contain only one dir

>&2 echo Verifying that $IMPORTABLE_PKG can be the target package...
>/dev/null stat ${SRC_DIR}/src/${IMPORTABLE_PKG}/*.p{y,yx,xd}

PYTHONS="$(ls -1 --ignore=cp34-cp34m /opt/python/ | sort -r)"
if [ -n "${PYTHON_TARGET}" ]
then
    if &>/dev/null grep -ow "^${PYTHON_TARGET}$" <<<"$PYTHONS"
    then
        >&2 echo Using the target Python requested \
            by the second argument ${PYTHON_TARGET}
        PYTHONS="${PYTHON_TARGET}"
    else
        >&2 echo Invalid Python target requested \
            by the second CLI argument ${PYTHON_TARGET}
        exit 1
    fi
else
    >&2 echo Using all Python targets found in this env
fi

>&2 echo Selected Python targets for this build run:
echo "${PYTHONS}" | >&2 tr ' ' '\n'


MANYLINUX_TAG="$(
    /opt/python/cp39-cp39/bin/python \
    "${IMAGE_SCRIPTS_DIR_PATH}/manylinux_mapping.py" \
    "${MANYLINUX_TARGET}"
)"


# Avoid creation of __pycache__/*.py[c|o]
export PYTHONDONTWRITEBYTECODE=1

import_userspace_tools

PIP_GLOBAL_ARGS=
if [ -n "$DEBUG" ]
then
    PIP_GLOBAL_ARGS=-vv
fi
GIT_GLOBAL_ARGS="--git-dir=${SRC_DIR}/.git --work-tree=${SRC_DIR}"
TESTS_SRC_DIR="${SRC_DIR}/tests"
BUILD_DIR=$(mktemp -d "/tmp/${DIST_NAME}-${MANYLINUX_TAG}-build.XXXXXXXXXX")
TESTS_DIR="${BUILD_DIR}/tests"
STATIC_DEPS_PREFIX="$(get_static_deps_dir)"

ORIG_WHEEL_DIR="${BUILD_DIR}/original-wheelhouse"
WHEEL_DEP_DIR="${BUILD_DIR}/deps-wheelhouse"
MANYLINUX_DIR="${BUILD_DIR}/manylinux-wheelhouse"
WHEELHOUSE_DIR="${SRC_DIR}/dist"
UNPACKED_WHEELS_DIR="${BUILD_DIR}/unpacked-wheels"
VENVS_DIR="${BUILD_DIR}/venvs"
ISOLATED_SRC_DIRS="${BUILD_DIR}/src"

# NOTE: `LDFLAGS` is necessary for the C-extension build's linker to
# NOTE: locate the symbols in the libssh shared object files.
# NOTE: Otherwise, the error is:
#
#   gcc -pthread -shared -lssh -I/opt/manylinux-static-deps.PPkLKziXI7/include -DCYTHON_TRACE=1 -DCYTHON_TRACE_NOGIL=1 /tmp/pip-req-build-4h841og7/src/tmpy3l03tmj/tmp/pip-req-build-4h841og7/src/pylibsshext/session.o -lssh -o build/lib.linux-x86_64-3.9/pylibsshext/session.cpython-39-x86_64-linux-gnu.so
#   /opt/rh/devtoolset-2/root/usr/libexec/gcc/x86_64-CentOS-linux/4.8.2/ld: cannot find -lssh
#   /opt/rh/devtoolset-2/root/usr/libexec/gcc/x86_64-CentOS-linux/4.8.2/ld: cannot find -lssh
#   collect2: error: ld returned 1 exit status
#   error: command '/opt/rh/devtoolset-2/root/usr/bin/gcc' failed with exit code 1
#   ----------------------------------------
#   ERROR: Failed building wheel for ansible-pylibssh
# Failed to build ansible-pylibssh
# ERROR: Failed to build one or more wheels
export LDFLAGS="'-L${STATIC_DEPS_PREFIX}/lib64' '-L${STATIC_DEPS_PREFIX}/lib'"

# NOTE: `LD_LIBRARY_PATH` is necessary so that `auditwheel repair` could locate `libssh.so.4`
export LD_LIBRARY_PATH="${STATIC_DEPS_PREFIX}/lib64:${STATIC_DEPS_PREFIX}/lib:$LD_LIBRARY_PATH"

ARCH=`uname -m`

>&2 echo
>&2 echo
>&2 echo ===============================================
>&2 echo Copying the source repo to temporary locations:
>&2 echo ===============================================
>&2 echo
for PY in $PYTHONS; do
    >&2 echo Creating "${ISOLATED_SRC_DIRS}/${PY}"...
    git ${GIT_GLOBAL_ARGS} worktree add --detach \
      "${ISOLATED_SRC_DIRS}/${PY}"
    cp -v "${PEP517_CONFIG_FILE}" "${ISOLATED_SRC_DIRS}/${PY}"/
done

>&2 echo
>&2 echo
>&2 echo ================
>&2 echo Building wheels:
>&2 echo ================
>&2 echo
export CFLAGS="'-I${STATIC_DEPS_PREFIX}/include'"
for PY in $PYTHONS; do
    PIP_BIN="/opt/python/${PY}/bin/pip"
    >&2 echo Using "${PIP_BIN}"...
    ${PIP_BIN} install -U 'pip >= 20' setuptools wheel ${PIP_GLOBAL_ARGS}
    ${PIP_BIN} wheel "${ISOLATED_SRC_DIRS}/${PY}" -w "${ORIG_WHEEL_DIR}" ${PIP_GLOBAL_ARGS}
done

>&2 echo
>&2 echo
>&2 echo ================
>&2 echo Reparing wheels:
>&2 echo ================
>&2 echo
# Bundle external shared libraries into the wheels
for PY in $PYTHONS; do
    for whl in ${ORIG_WHEEL_DIR}/${DIST_NAME}-*-${PY}-linux_${ARCH}.whl; do
        >&2 echo Reparing "${whl}" for "${MANYLINUX_TAG}"...
        auditwheel repair --only-plat --plat "${MANYLINUX_TARGET}" "${whl}" -w ${MANYLINUX_DIR}
    done
done

# Download deps
>&2 echo
>&2 echo
>&2 echo =========================
>&2 echo Downloading dependencies:
>&2 echo =========================
>&2 echo
for PY in $PYTHONS; do
    for WHEEL_FILE in `ls ${MANYLINUX_DIR}/${DIST_NAME}-*-${PY}-${MANYLINUX_TAG}.whl`; do
        PIP_BIN="/opt/python/${PY}/bin/pip"
        >&2 echo Downloading ${WHEEL_FILE} deps using ${PIP_BIN}...
        ${PIP_BIN} download -d "${WHEEL_DEP_DIR}" "${WHEEL_FILE}" ${PIP_GLOBAL_ARGS}
    done
done

>&2 echo
>&2 echo ===================
>&2 echo Creating test venvs
>&2 echo ===================
>&2 echo
for PY in $PYTHONS; do
    VENV_NAME="${PY}-${MANYLINUX_TAG}"
    VENV_PATH="${VENVS_DIR}/${VENV_NAME}"
    VENV_BIN="/opt/python/${PY}/bin/virtualenv"

    >&2 echo
    >&2 echo Creating a venv at ${VENV_PATH}...
    ${VENV_BIN} "${VENV_PATH}"
done

# Install packages
>&2 echo
>&2 echo
>&2 echo ============================
>&2 echo Testing wheels installation:
>&2 echo ============================
>&2 echo
for PY in $PYTHONS; do
    VENV_NAME="${PY}-${MANYLINUX_TAG}"
    VENV_PATH="${VENVS_DIR}/${VENV_NAME}"
    PIP_BIN="${VENV_PATH}/bin/pip"
    >&2 echo Using ${PIP_BIN}...
    ${PIP_BIN} install --no-compile "${DIST_NAME}" --no-index -f "${MANYLINUX_DIR}/" ${PIP_GLOBAL_ARGS}
done

>&2 echo
>&2 echo ==============
>&2 echo WHEEL ANALYSIS
>&2 echo ==============
>&2 echo
for PY in $PYTHONS; do
    WHEEL_BIN="/opt/python/${PY}/bin/wheel"
    PLAT_TAG="${PY}-${MANYLINUX_TAG}"
    UNPACKED_DIR=${UNPACKED_WHEELS_DIR}/${PLAT_TAG}
    WHEEL_FILE=`ls ${MANYLINUX_DIR}/${DIST_NAME}-*-${PLAT_TAG}.whl`
    >&2 echo
    >&2 echo Analysing ${WHEEL_FILE}...
    auditwheel show "${WHEEL_FILE}"
    ${WHEEL_BIN} unpack -d "${UNPACKED_DIR}" "${WHEEL_FILE}"
    # chmod avoids ldd warning about files being non-executable:
    chmod +x "${UNPACKED_DIR}"/${DIST_NAME}-*/{${DIST_NAME}.libs/*.so.*,${IMPORTABLE_PKG}/*.so}
    >&2 echo Verifying that all links in '`*.so`' files of ${WHEEL_FILE} exist...
    ! ldd "${UNPACKED_DIR}"/${DIST_NAME}-*/{${DIST_NAME}.libs/*.so.*,${IMPORTABLE_PKG}/*.so} | grep '=> not found'
done

>&2 echo
>&2 echo
>&2 echo ===================================
>&2 echo Running smoke tests against wheels:
>&2 echo ===================================
>&2 echo
cp -vr "${TESTS_SRC_DIR}" "${TESTS_DIR}"
sed \
  's#\s\+--cov.*##;s#\s\+--no-cov-on-fail.*##;s#\s\+-p\spytest_cov.*##' \
  "${SRC_DIR}/pytest.ini" > "${TESTS_DIR}/pytest.ini"
pushd "${TESTS_DIR}"
for PY_BIN in `ls ${VENVS_DIR}/*/bin/python`; do
    $PY_BIN -B -m pip install --no-compile pytest pytest-forked pytest-xdist ${PIP_GLOBAL_ARGS}
    $PY_BIN -B -m pytest -m smoke "${TESTS_DIR}"
done
popd

>&2 echo
>&2 echo
>&2 echo ==================
>&2 echo SELF-TEST COMPLETE
>&2 echo ==================
>&2 echo

>&2 echo Copying built manylinux wheels back to the host...
chown -R --reference="${PERM_REF_HOST_FILE}" "${MANYLINUX_DIR}"/*
mkdir -pv "${WHEELHOUSE_DIR}"
chown --reference="${PERM_REF_HOST_FILE}" "${WHEELHOUSE_DIR}"
cp -av "${MANYLINUX_DIR}"/"${DIST_NAME}"-*-${MANYLINUX_TAG}.whl "${WHEELHOUSE_DIR}/"
>&2 echo Final OS-specific wheels for ${DIST_NAME}:
ls -l ${WHEELHOUSE_DIR}
