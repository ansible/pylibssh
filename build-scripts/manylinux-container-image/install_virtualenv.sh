#!/bin/bash
set -xe

for python in /opt/python/*; do
    "$python/bin/pip" install virtualenv
done
