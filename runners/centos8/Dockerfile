FROM centos:8
ARG FIPS

# This is needed because otherwise `sys.getfilesystemencoding()` returns
# "ANSI_X3.4-1968".
ENV LANG C.UTF-8

# Also add a travis user
RUN groupadd -g 2000 travis
RUN useradd -u 2000 -g 2000 -m -s /bin/bash travis

RUN yum install -y gcc libffi-devel python2-devel python3-devel openssl-devel git which

RUN if [ "$FIPS" = "1" ] ; then touch /etc/system-fips && echo "FIPS mode"; else echo "Not FIPS mode"; fi

RUN curl -sSL https://bootstrap.pypa.io/get-pip.py | python2

RUN pip install -q tox
