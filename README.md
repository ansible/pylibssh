# Python Cryptographic Authority Infrastructure

The [PyCA](https://github.com/pyca) operates a significant amount of
infrastructure in the form of continuous integration. This repository holds the
configuration for setting up Jenkins, as well as the various docker containers
we use in testing.

**This is a work in progress and the [new CI](https://ci.cryptography.io)
**server is not yet primary.**

## Ansible

To run the ansible playbook you'll need your SSH public key in the server's
`authorized_keys` and then you can run `./deploy`.

Ansible is responsible for making sure Docker is running on the host,
installing SystemD service files for Caddy and Jenkins, pulling the Caddy and
Jenkins docker images, and making sure they're running.

## Docker Containers

Docker containers are built on merge by [Docker
Hub](https://hub.docker.com/u/pyca/). Each repository on Docker Hub corresponds
to a directory in `runners`.
