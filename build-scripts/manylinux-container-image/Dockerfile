ARG RELEASE
FROM quay.io/pypa/${RELEASE}
ARG RELEASE
ARG LIBSSH_VERSION=0.9.4
MAINTAINER Python Cryptographic Authority
WORKDIR /root
RUN \
  if [ $(uname -m) = "x86_64" ]; \
  then \
    if stat /etc/redhat-release 1>&2 2>/dev/null; then \
      yum -y install prelink && \
      yum -y clean all && \
      rm -rf /var/cache/yum; \
    else \
      export DEBIAN_FRONTEND=noninteractive && \
      apt-get update -qq && \
      apt-get install -qq -y --no-install-recommends prelink && \
      apt-get clean -qq && \
      rm -rf /var/lib/apt/lists/*; \
    fi; \
  fi
ADD install_perl.sh /root/install_perl.sh
RUN ./install_perl.sh
ADD install_libffi.sh /root/install_libffi.sh
RUN ./install_libffi.sh "${RELEASE}"
ADD install_openssl.sh /root/install_openssl.sh
ADD openssl-version.sh /root/openssl-version.sh
RUN ./install_openssl.sh

ADD install_virtualenv.sh /root/install_virtualenv.sh
RUN ./install_virtualenv.sh

# Install PyPy
RUN if [ $(uname -m) = "x86_64" ]; then curl https://downloads.python.org/pypy/pypy3.6-v7.3.3-linux64.tar.bz2 | tar jxf - -C /opt/ && mv /opt/pypy3.6* /opt/pypy3.6; fi
RUN if [ $(uname -m) = "x86_64" ]; then curl https://downloads.python.org/pypy/pypy3.7-v7.3.3-linux64.tar.bz2 | tar jxf - -C /opt/ && mv /opt/pypy3.7* /opt/pypy3.7; fi

RUN if ! [[ ${RELEASE} =~ '^manylinux1_.*$' ]]; then curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable --profile minimal; fi
ENV PATH="/root/.cargo/bin:$PATH"

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
