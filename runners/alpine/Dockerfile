FROM alpine:latest

# Increment this to blow away the docker cache
ENV CACHE_BUSTER 1

# This is needed because otherwise `sys.getfilesystemencoding()` returns
# "ANSI_X3.4-1968".
ENV LANG C.UTF-8

RUN apk add --no-cache git libffi-dev curl \
    python3-dev libressl-dev bash gcc musl-dev

RUN curl -sSL https://bootstrap.pypa.io/get-pip.py | python3

RUN pip install tox coverage

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable
ENV PATH="/root/.cargo/bin:$PATH"
