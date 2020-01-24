# -*- coding: utf-8 -*-

"""Dist metadata setup."""

import os
import sys
from glob import glob

from setuptools import setup
from setuptools.extension import Extension

from Cython.Build import cythonize

LIB_NAME = 'ssh'

sys.path.insert(0, os.path.abspath('src'))


def _get_sources(path):
    return glob(path)


def _get_names(sources):
    names = []
    for src in sources:
        src_lst = src.replace(os.path.sep, '.')
        name_lst = src_lst.split('.')[1:-1]
        names.append('.'.join(name_lst))
    return names


def _get_extensions():
    extensions = []
    sources = _get_sources('src/pylibsshext/*.pyx')
    names = _get_names(sources)

    for index, src in enumerate(sources):
        extensions.append(Extension(names[index], [src], libraries=[LIB_NAME]))
    return extensions


__name__ == '__main__' and setup(  # noqa: WPS428
    ext_modules=cythonize(_get_extensions()),
)
