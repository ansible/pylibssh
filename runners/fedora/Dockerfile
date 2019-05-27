FROM registry.fedoraproject.org/fedora:latest

# This is needed because otherwise `sys.getfilesystemencoding()` returns
# "ANSI_X3.4-1968".
ENV LANG C.UTF-8

# also add a travis user
RUN groupadd -g 2000 travis
RUN useradd -u 2000 -g 2000 -m -s /bin/bash travis

RUN dnf install -y gcc redhat-rpm-config libffi-devel python-devel \
    python3-devel openssl-devel git findutils which

RUN curl -sSL https://bootstrap.pypa.io/get-pip.py | python

RUN pip install -q tox
