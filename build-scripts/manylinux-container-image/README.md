# manylinux images

This is a container definition based on the great work of folks
maintaining [PyCA/infra]. It is dual-licensed under Apache 2.0 and
BSD 3-clause. The corresponding license files are present in
this directory.

## Docker Containers

Docker containers are rebuilt on cron by Github Actions and then
uploaded to [Github Container Registry].

## Building locally

It is possible to build a container locally by running something like

```console
$ podman build --build-arg RELEASE=manylinux1_x86_64 .
```

> *NOTE:* The base image is parametrised with a `--build-arg` option and> is constructed as `quay.io/pypa/${RELEASE}`.

[Github Container Registry]: https://github.com/orgs/ansible/packages?ecosystem=container&visibility=all
[PyCA/infra]: https://github.com/pyca/infra
