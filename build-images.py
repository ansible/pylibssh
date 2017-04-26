#!/usr/bin/env python

import collections
import json
import os
import subprocess


Image = collections.namedtuple("Image", ["tag", "path", "build_args"])

IMAGES = []

with open("config.json") as config:
    for conf in json.load(config):
        IMAGES.append(
            Image(
                tag=conf['tag'],
                path=conf['path'],
                build_args=conf['build_args']
            )
        )


def docker_build(image):
    full_path = os.path.join(os.path.dirname(__file__), image.path)
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
