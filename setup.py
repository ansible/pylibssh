# -*- coding: utf-8 -*-

"""Dist metadata setup."""

import os
import sys

from glob import glob
from setuptools import setup
from setuptools.extension import Extension

from Cython.Build import cythonize

LIB_NAME = 'ssh'

sys.path.insert(0, os.path.abspath('lib'))

sources = glob('lib/pylibssh/*.pyx')
names = ['.'.join(src.replace(os.path.sep, '.').split('.')[1:-1]) for src in sources]
extensions = [Extension(names[i], [sources[i]], libraries=[LIB_NAME]) for i in range(len(sources))]

__name__ == '__main__' and setup(  # noqa: WPS428
    ext_modules=cythonize(extensions)
)
