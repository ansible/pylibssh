FROM centos:8
ARG FIPS

# This is needed because otherwise `sys.getfilesystemencoding()` returns
# "ANSI_X3.4-1968".
ENV LANG C.UTF-8

RUN yum install -y gcc libffi-devel python3-devel openssl-devel git which

RUN if [ "$FIPS" = "1" ] ; then touch /etc/system-fips && echo "FIPS mode"; else echo "Not FIPS mode"; fi

RUN curl -sSL https://bootstrap.pypa.io/get-pip.py | python3

RUN pip install tox coverage

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable --profile minimal
ENV PATH="/root/.cargo/bin:$PATH"
