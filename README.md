# Python Cryptographic Authority Infrastructure

The [PyCA](https://github.com/pyca) has a significant amount of automation
to support our robust continuous integration. This repository holds the
configuration for building the various docker containers we use in testing,
as well as OpenSSL binaries we use.

## Docker Containers

Docker containers are built on merge by Github Actions and then uploaded to
[Docker Hub](https://hub.docker.com/u/pyca/). Each repository on Docker Hub
corresponds to a directory in `runners`.

