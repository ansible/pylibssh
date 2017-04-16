#!/usr/bin/env python

import collections
import os
import subprocess


Image = collections.namedtuple("Image", ["tag", "path", "build_args"])

IMAGES = [
    Image(
        tag="crypto-jenkins", path=["jenkins"], build_args=[]
    ),
    Image(
        tag="caddy", path=["caddy"], build_args=[]
    ),
    Image(
        tag="cryptography-runner-centos7:latest",
        path=["runners", "centos7"],
        build_args=[]
    ),
    Image(
        tag="cryptography-runner-jessie:latest",
        path=["runners", "jessie"],
        build_args=[]
    ),
    Image(
        tag="cryptography-runner-stretch:latest",
        path=["runners", "stretch"],
        build_args=[]
    ),
    Image(
        tag="cryptography-runner-sid:latest",
        path=["runners", "sid"],
        build_args=[]
    ),
    Image(
        tag="cryptography-runner-jessie-libressl:2.4.5",
        path=["runners", "jessie-libressl"],
        build_args=["LIBRE_VERSION=2.4.5"],
    ),
    Image(
        tag="cryptography-runner-jessie-libressl:2.5.3",
        path=["runners", "jessie-libressl"],
        build_args=["LIBRE_VERSION=2.5.3"],
    ),
]


def docker_build(image):
    full_path = os.path.join(os.path.dirname(__file__), *image.path)
    shell_cmd = ["docker", "build", "-t", image.tag, full_path]
    for build_arg in image.build_args:
        shell_cmd += ["--build-arg", build_arg]

    subprocess.check_call(shell_cmd)


def main():
    for image in IMAGES:
        print("=== Building {}".format(image.tag))
        docker_build(image)


if __name__ == "__main__":
    main()
