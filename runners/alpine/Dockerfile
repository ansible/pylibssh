FROM alpine:latest

ARG user=jenkins
ARG group=jenkins
ARG uid=1000
ARG gid=1000

# Increment this to blow away the docker cache
ENV CACHE_BUSTER 1

# This is needed because otherwise `sys.getfilesystemencoding()` returns
# "ANSI_X3.4-1968".
ENV LANG C.UTF-8

# Docker pipeline plugin mounts the workspace into the image
# This adds the same uid/gid that we use in the jenkins container
# so getpwuid() won't fail when tox invokes
RUN addgroup -g ${gid} ${group}
RUN adduser -u ${uid} -G ${group} -D ${user}
# Also add a travis user
RUN addgroup -g 2000 travis
RUN adduser -u 2000 -G travis -D travis

RUN apk add --no-cache git libffi-dev curl python-dev \
    python3-dev libressl-dev bash gcc musl-dev

RUN curl -sSL https://bootstrap.pypa.io/get-pip.py | python

RUN pip install -q tox

USER jenkins
