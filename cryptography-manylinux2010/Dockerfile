FROM quay.io/pypa/manylinux2010_x86_64
MAINTAINER Python Cryptographic Authority
WORKDIR /root
RUN yum -y install prelink && yum -y clean all
ADD install_libffi.sh /root/install_libffi.sh
RUN sh install_libffi.sh
ADD install_openssl.sh /root/install_openssl.sh
RUN sh install_openssl.sh
ADD install_virtualenv.sh /root/install_virtualenv.sh
RUN sh install_virtualenv.sh
