export OPENSSL_VERSION="openssl-1.1.1i"
export OPENSSL_SHA256="e8be6a35fe41d10603c3cc635e93289ed00bf34b79671a3a4de64fcee00d5242"
# We need a base set of flags because on Windows using MSVC
# enable-ec_nistp_64_gcc_128 doesn't work since there's no 128-bit type
export OPENSSL_BUILD_FLAGS_WINDOWS="no-ssl3 no-ssl3-method no-zlib no-shared no-comp no-dynamic-engine"
export OPENSSL_BUILD_FLAGS="${OPENSSL_BUILD_FLAGS_WINDOWS} enable-ec_nistp_64_gcc_128"
