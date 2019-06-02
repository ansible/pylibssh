# Python Cryptographic Authority Infrastructure

The [PyCA](https://github.com/pyca) operates a significant amount of
infrastructure in the form of continuous integration. This repository holds the
configuration for building the various docker containers we use in testing, as
well as wheel builders for external projects.

## Ansible

To run the ansible playbook you'll need your SSH public key in the server's
`authorized_keys` and then you can run `./deploy`.

Ansible is responsible for making sure Docker is running on the host,
installing SystemD service files for Caddy, pulling the Caddy docker images, and
making sure it's running.

## Docker Containers

Docker containers are built on merge by Azure Pipelines and then uploaded to [Docker
Hub](https://hub.docker.com/u/pyca/). Each repository on Docker Hub corresponds
to a directory in `runners`.

