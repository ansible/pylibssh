FROM alpine:latest

# Increment this to blow away the docker cache
ENV CACHE_BUSTER 1

# This is needed because otherwise `sys.getfilesystemencoding()` returns
# "ANSI_X3.4-1968".
ENV LANG C.UTF-8

# Also add a travis user
RUN addgroup -g 2000 travis
RUN adduser -u 2000 -G travis -D travis

RUN apk add --no-cache git libffi-dev curl python-dev \
    python3-dev libressl-dev bash gcc musl-dev

RUN curl -sSL https://bootstrap.pypa.io/get-pip.py | python

RUN pip install -q tox
