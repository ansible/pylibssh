#!/bin/bash
set -x

LIB_VERSION="$1"

set -Eeuo pipefail

unset RELEASE

source get-static-deps-dir.sh

LIB_NAME=libssh
BUILD_DIR=$(mktemp -d "/tmp/${LIB_NAME}-${LIB_VERSION}-manylinux-build.XXXXXXXXXX")

LIB_CLONE_DIR="${BUILD_DIR}/${LIB_NAME}-${LIB_VERSION}"
LIB_BUILD_DIR="${LIB_CLONE_DIR}/build"

STATIC_DEPS_PREFIX="$(get_static_deps_dir)"

if [ -z "${LIB_VERSION}" ]
then
    >&2 echo "Please pass libssh version as a first argument of this script (${0})"
    exit 1
fi

# NOTE: `LDFLAGS` is necessary for the linker to locate the symbols for
# NOTE: things like `dlopen', `dlclose', `pthread_atfork', `dlerror',
# NOTE: `dlsym', `dladdr' etc.
# NOTE: Otherwise, the build failure looks as follows:
#
# [ 66%] Linking C executable libssh_scp
# ../lib/libssh.so.4.8.5: undefined reference to `dlopen'
# ../lib/libssh.so.4.8.5: undefined reference to `dlclose'
# ../lib/libssh.so.4.8.5: undefined reference to `pthread_atfork'
# ../lib/libssh.so.4.8.5: undefined reference to `dlerror'
# ../lib/libssh.so.4.8.5: undefined reference to `dlsym'
# ../lib/libssh.so.4.8.5: undefined reference to `dladdr'
# collect2: error: ld returned 1 exit status
# make[2]: *** [examples/libssh_scp] Error 1
# make[1]: *** [examples/CMakeFiles/libssh_scp.dir/all] Error 2
# make: *** [all] Error 2
export LDFLAGS="-pthread -ldl"

# NOTE: `PKG_CONFIG_PATH` is necessary for `cmake` to be able to locate
# NOTE: C-headers files `*.h`. Otherwise, the error is:
#
# -- Found ZLIB: /opt/manylinux-static-deps.PPkLKziXI7/lib/libz.a (found version "1.2.11")
# -- Could NOT find OpenSSL, try to set the path to OpenSSL root folder in the system variable OPENSSL_ROOT_DIR (missing: OPENSSL_CRYPTO_LIBRARY OPENSSL_INCLUDE_DIR)
# -- Could NOT find GCrypt, try to set the path to GCrypt root folder in the system variable GCRYPT_ROOT_DIR (missing: GCRYPT_INCLUDE_DIR GCRYPT_LIBRARIES)
# CMake Warning (dev) at /root/.tools-venv/lib/python3.9/site-packages/cmake/data/share/cmake-3.18/Modules/FindPackageHandleStandardArgs.cmake:273 (message):
#   The package name passed to `find_package_handle_standard_args` (MBedTLS)
#   does not match the name of the calling package (MbedTLS).  This can lead to
#   problems in calling code that expects `find_package` result variables
#   (e.g., `_FOUND`) to follow a certain pattern.
# Call Stack (most recent call first):
#   cmake/Modules/FindMbedTLS.cmake:96 (find_package_handle_standard_args)
#   CMakeLists.txt:65 (find_package)
# This warning is for project developers.  Use -Wno-dev to suppress it.
#
# -- Could NOT find mbedTLS, try to set the path to mbedLS root folder in
#         the system variable MBEDTLS_ROOT_DIR (missing: MBEDTLS_INCLUDE_DIR MBEDTLS_LIBRARIES)
# CMake Error at CMakeLists.txt:67 (message):
#   Could not find OpenSSL, GCrypt or mbedTLS
#
#
# -- Configuring incomplete, errors occurred!
# See also "/tmp/libssh-0.9.4-manylinux-build.FJUercWAg9/libssh-0.9.4/build/CMakeFiles/CMakeOutput.log".
# See also "/tmp/libssh-0.9.4-manylinux-build.FJUercWAg9/libssh-0.9.4/build/CMakeFiles/CMakeError.log".
export PYCA_OPENSSL_PATH=/opt/pyca/cryptography/openssl
export PKG_CONFIG_PATH="${STATIC_DEPS_PREFIX}/lib64/pkgconfig:${STATIC_DEPS_PREFIX}/lib/pkgconfig:${PYCA_OPENSSL_PATH}/lib/pkgconfig"

>&2 echo
>&2 echo
>&2 echo ==================================================
>&2 echo downloading source of ${LIB_NAME} v${LIB_VERSION}:
>&2 echo ==================================================
>&2 echo
git clone \
    --depth=1 \
    -b "${LIB_NAME}-${LIB_VERSION}" \
    https://git.libssh.org/projects/${LIB_NAME}.git \
    "${LIB_CLONE_DIR}"

source activate-userspace-tools.sh
import_userspace_tools

mkdir -pv "${LIB_BUILD_DIR}"
pushd "${LIB_BUILD_DIR}"
# For some reason, libssh has to be compiled as a shared object.
# If not, imports fail at runtime, with undefined symbols:
# ```python-traceback
# test/units/test_sftp.py:7: in <module>
#     from pylibsshext.sftp import SFTP
# E   ImportError: /opt/python/cp27-cp27m/lib/python2.7/site-packages/pylibsshext/sftp.so: undefined symbol: sftp_get_error
# ```
# Also, when compiled statically, manylinux2010 container turns dist
# into manylinux1 but because of the reason above, it doesn't make sense.
cmake "${LIB_CLONE_DIR}" \
    -DCMAKE_INSTALL_PREFIX="${STATIC_DEPS_PREFIX}" \
    -DCMAKE_BUILD_TYPE=MinSizeRel \
    -DBUILD_SHARED_LIBS=ON \
    -DCLIENT_TESTING=OFF \
    -DSERVER_TESTING=OFF \
    -DUNIT_TESTING=OFF \
    -DWITH_GSSAPI=ON \
    -DWITH_SERVER=OFF \
    -DWITH_PCAP=OFF \
    -DWITH_ZLIB=ON
make
make install/strip
popd

rm -rf "${BUILD_DIR}"
