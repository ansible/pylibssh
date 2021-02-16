export OPENSSL_VERSION="openssl-1.1.1j"
export OPENSSL_SHA256="aaf2fcb575cdf6491b98ab4829abf78a3dec8402b8b81efc8f23c00d443981bf"
# We need a base set of flags because on Windows using MSVC
# enable-ec_nistp_64_gcc_128 doesn't work since there's no 128-bit type
export OPENSSL_BUILD_FLAGS_WINDOWS="no-ssl3 no-ssl3-method no-zlib no-shared no-comp no-dynamic-engine"
export OPENSSL_BUILD_FLAGS="${OPENSSL_BUILD_FLAGS_WINDOWS} enable-ec_nistp_64_gcc_128"
