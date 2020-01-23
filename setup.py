# -*- coding: utf-8 -*-

"""Dist metadata setup."""

import os
from glob import glob

from setuptools import setup
from setuptools.extension import Extension

from Cython.Build import cythonize

IMPORTABLE_PATH_SEP = '.'
LIB_DIR = 'src'
LIB_NAME = 'ssh'


def _path_to_imp(path):
    return os.path.splitext(path)[0].replace(os.path.sep, IMPORTABLE_PATH_SEP)


def _get_src_map(src_glob):
    sources = glob(src_glob)  # src file list

    for src in sources:  # noqa: WPS526
        yield _path_to_imp(src), src


def _get_extensions():
    src_map = _get_src_map(os.path.join(LIB_DIR, '**/*.pyx'))

    for name, src in src_map:  # noqa: WPS526
        yield Extension(name, [src], libraries=[LIB_NAME])


def _cythonize_extensions():
    return cythonize(list(_get_extensions()))


__name__ == '__main__' and setup(  # noqa: WPS428
    ext_modules=_cythonize_extensions(),
)
