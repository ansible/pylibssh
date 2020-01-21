# -*- coding: utf-8 -*-

"""Dist metadata setup."""

import os
import sys

from Cython.Build import cythonize
from setuptools import find_packages, setup
from setuptools.extension import Extension

LIB_NAME = 'ssh'


sys.path.insert(0, os.path.abspath('lib'))

setup(
    name='pylibssh',
    version='0.0.1.dev0',
    ext_modules=cythonize([
        Extension('pylibssh.session', ['lib/pylibssh/session.pyx'], libraries=[LIB_NAME]),
        Extension('pylibssh.channel', ['lib/pylibssh/channel.pyx'], libraries=[LIB_NAME]),
        Extension('pylibssh.sftp', ['lib/pylibssh/sftp.pyx'], libraries=[LIB_NAME]),
        Extension('pylibssh.errors', ['lib/pylibssh/errors.pyx'], libraries=[LIB_NAME]),
    ]),
    package_dir={'': 'lib'},
    packages=find_packages('lib'),
    description='Python bindings for libssh client',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Cython',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Security',
    ],
)
