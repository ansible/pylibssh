ARG RELEASE
FROM quay.io/pypa/${RELEASE}
ARG RELEASE
ARG LIBSSH_VERSION=0.9.4
MAINTAINER Python Cryptographic Authority
WORKDIR /root

ADD update-packages.sh /root/update-packages.sh
RUN ./update-packages.sh

ADD build_utils.sh /root/build_utils.sh
ADD install_perl.sh /root/install_perl.sh
RUN ./install_perl.sh "${RELEASE}"
ADD install_libffi.sh /root/install_libffi.sh
RUN ./install_libffi.sh "${RELEASE}"
ADD install_openssl.sh /root/install_openssl.sh
ADD openssl-version.sh /root/openssl-version.sh
RUN ./install_openssl.sh "${RELEASE}"

ADD install_virtualenv.sh /root/install_virtualenv.sh
RUN ./install_virtualenv.sh

# \pylibssh
ADD install-userspace-tools.sh /root/install-userspace-tools.sh
ADD activate-userspace-tools.sh /root/activate-userspace-tools.sh
RUN ./install-userspace-tools.sh
ADD make-static-deps-dir.sh /root/make-static-deps-dir.sh
ADD get-static-deps-dir.sh /root/get-static-deps-dir.sh
RUN ./make-static-deps-dir.sh
ADD install_zlib.sh /root/install_zlib.sh
RUN ./install_zlib.sh
ADD install_libssh.sh /root/install_libssh.sh
RUN ./install_libssh.sh "${LIBSSH_VERSION}"
# /pylibssh
