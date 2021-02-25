ARG RELEASE
FROM quay.io/pypa/${RELEASE}
ARG RELEASE
MAINTAINER Python Cryptographic Authority
WORKDIR /root
RUN if [ $(uname -m) = "x86_64" ]; then yum -y install prelink && yum -y clean all; fi
ADD install_perl.sh /root/install_perl.sh
RUN sh install_perl.sh
ADD install_libffi.sh /root/install_libffi.sh
RUN sh install_libffi.sh "${RELEASE}"
ADD install_openssl.sh /root/install_openssl.sh
ADD openssl-version.sh /root/openssl-version.sh
RUN sh install_openssl.sh

ADD install_virtualenv.sh /root/install_virtualenv.sh
RUN sh install_virtualenv.sh

# Install PyPy
RUN if [ $(uname -m) = "x86_64" ]; then curl https://downloads.python.org/pypy/pypy3.6-v7.3.3-linux64.tar.bz2 | tar jxf - -C /opt/ && mv /opt/pypy3.6* /opt/pypy3.6; fi
RUN if [ $(uname -m) = "x86_64" ]; then curl https://downloads.python.org/pypy/pypy3.7-v7.3.3-linux64.tar.bz2 | tar jxf - -C /opt/ && mv /opt/pypy3.7* /opt/pypy3.7; fi

RUN if ! [[ ${RELEASE} =~ '^manylinux1_.*$' ]]; then curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable --profile minimal; fi
ENV PATH="/root/.cargo/bin:$PATH"
