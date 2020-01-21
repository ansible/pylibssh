# -*- coding: utf-8 -*-

"""Dist metadata setup."""

import os
import sys

from setuptools import setup
from setuptools.extension import Extension

from Cython.Build import cythonize

LIB_NAME = 'ssh'


sys.path.insert(0, os.path.abspath('lib'))


__name__ == '__main__' and setup(  # noqa: WPS428
    ext_modules=cythonize([
        Extension(
            'pylibssh.session', ['lib/pylibssh/session.pyx'], libraries=[LIB_NAME],
        ),
        Extension(
            'pylibssh.channel', ['lib/pylibssh/channel.pyx'], libraries=[LIB_NAME],
        ),
        Extension(
            'pylibssh.sftp', ['lib/pylibssh/sftp.pyx'], libraries=[LIB_NAME],
        ),
        Extension(
            'pylibssh.errors', ['lib/pylibssh/errors.pyx'], libraries=[LIB_NAME],
        ),
    ]),
)
