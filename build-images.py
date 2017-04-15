#!/usr/bin/env python

import subprocess


IMAGES = [
    ("jenkins", "crypto-jenkins"),
    ("caddy", "caddy"),
]


def docker_build(path, tag):
    subprocess.check_call(["docker", "build", "-t", tag, path])


def main():
    for path, tag_name in IMAGES:
        print("=== Building {}".format(path))
        docker_build(path, tag=tag_name)


if __name__ == "__main__":
    main()
