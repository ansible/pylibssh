FROM alpine:latest

# Increment this to blow away the docker cache
ENV CACHE_BUSTER 1

# This is needed because otherwise `sys.getfilesystemencoding()` returns
# "ANSI_X3.4-1968".
ENV LANG C.UTF-8

# Also add a travis user
RUN addgroup -g 2000 travis
RUN adduser -u 2000 -G travis -D travis

RUN apk add --no-cache git libffi-dev curl \
    python3-dev libressl-dev bash gcc musl-dev

RUN curl -sSL https://bootstrap.pypa.io/get-pip.py | python3

RUN pip install -q tox

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable
ENV PATH="$HOME/.cargo/bin:$PATH"
