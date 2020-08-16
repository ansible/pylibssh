FROM registry.fedoraproject.org/fedora:latest

# This is needed because otherwise `sys.getfilesystemencoding()` returns
# "ANSI_X3.4-1968".
ENV LANG C.UTF-8

RUN dnf install -y gcc redhat-rpm-config libffi-devel python python-devel \
    python3-devel openssl-devel git findutils which

RUN curl -sSL https://bootstrap.pypa.io/get-pip.py | python

RUN pip install -q tox

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable
ENV PATH="/root/.cargo/bin:$PATH"
