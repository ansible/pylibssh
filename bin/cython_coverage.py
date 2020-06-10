# -*- coding: utf-8 -*-
"""
A patched Cython plugin for coverage.py.

Ref: https://github.com/cython/cython/issues/3636
Ref: https://github.com/cython/cython/pull/3648

Requires the coverage package at least in version 4.0 (which added the plugin API).
"""

from __future__ import absolute_import

import os.path  # noqa: WPS301
import sys

import Cython.Coverage  # noqa: WPS301
from coverage.files import canonical_filename
from Cython.Coverage import Plugin as OriginalCythonCoveragePlugin


def _ptchd_fnd_dep_file_pth(  # noqa: WPS231, WPS317
        main_file, file_path,  # noqa: WPS318
        relative_path_search=False,  # noqa: WPS317
):
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path) and (  # noqa: WPS337
            file_path.endswith('.pxi') or  # noqa: WPS318
            relative_path_search
    ):
        # files are looked up relative to the main source file
        rel_file_path = os.path.join(os.path.dirname(main_file), file_path)
        if os.path.exists(rel_file_path):
            abs_path = os.path.abspath(rel_file_path)

        # when file_path matches the main_file ending, that's it:
        matching_abs_path = ''.join((
            os.path.splitext(main_file)[0],
            os.path.splitext(file_path)[1],
        ))
        if matching_abs_path.endswith(file_path):
            return matching_abs_path

    # search sys.path for external locations if a valid file hasn't been found
    if not os.path.exists(abs_path):
        for sys_path in sys.path:
            test_path = os.path.realpath(os.path.join(sys_path, file_path))
            if os.path.exists(test_path):
                return canonical_filename(test_path)
    return canonical_filename(abs_path)


Cython.Coverage._find_dep_file_path = _ptchd_fnd_dep_file_pth  # noqa: WPS437


class PatchedCythonCoveragePlugin(OriginalCythonCoveragePlugin):
    """Patched Cython coverage plugin implementation."""


def coverage_init(reg, options):
    """Register the patched coverage plugin implementation."""
    reg.add_file_tracer(PatchedCythonCoveragePlugin())
