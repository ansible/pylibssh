FROM centos:8

# This is needed because otherwise `sys.getfilesystemencoding()` returns
# "ANSI_X3.4-1968".
ENV LANG C.UTF-8

# Also add a travis user
RUN groupadd -g 2000 travis
RUN useradd -u 2000 -g 2000 -m -s /bin/bash travis

# This will allow us to do some FIPS testing in conjunction with
# OPENSSL_FORCE_FIPS_MODE in CentOS
RUN touch /etc/system-fips

RUN yum install -y gcc libffi-devel python2-devel python3-devel openssl-devel git which

RUN curl -sSL https://bootstrap.pypa.io/get-pip.py | python2

RUN pip install -q tox
