# -*- coding: utf-8 -*-

"""PEP 517 build backend pre-building Cython exts before setuptools."""

from __future__ import (  # noqa: WPS422
    absolute_import, division, print_function,
)

import contextlib
import functools
import os
import sys
from itertools import chain

import toml
from expandvars import expandvars
from setuptools.build_meta import (
    build_sdist, build_wheel, get_requires_for_build_sdist,
    get_requires_for_build_wheel, prepare_metadata_for_build_wheel,
)


# isort: split
from distutils.command.install import install as distutils_install_cmd
from distutils.core import Distribution as distutils_distribution  # noqa: N813

from Cython.Build.Cythonize import main as cythonize_cli_cmd


__all__ = (  # noqa: WPS317, WPS410
    'build_sdist', 'build_wheel', 'get_requires_for_build_sdist',
    'get_requires_for_build_wheel', 'prepare_metadata_for_build_wheel',
)

__metadata__ = type  # pylint: disable=invalid-name  # make classes new-style


def get_config():
    """Grab optional build dependencies from pyproject.toml config.

    :returns: config section from ``pyproject.toml``
    :rtype: dict

    This basically reads entries from::

        [tool.local.cythonize]
        # Env vars provisioned during cythonize call
        src = ["src/**/*.pyx"]

        [tool.local.cythonize.env]
        # Env vars provisioned during cythonize call
        LDFLAGS = "-lssh"

        [tool.local.cythonize.flags]
        # This section can contain the following booleans:
        # * annotate — generate annotated HTML page for source files
        # * build — build extension modules using distutils
        # * inplace — build extension modules in place using distutils (implies -b)
        # * force — force recompilation
        # * quiet — be less verbose during compilation
        # * lenient — increase Python compat by ignoring some compile time errors
        # * keep-going — compile as much as possible, ignore compilation failures
        annotate = false
        build = false
        inplace = true
        force = true
        quiet = false
        lenient = false
        keep-going = false

        [tool.local.cythonize.kwargs]
        # This section can contain args tha have values:
        # * exclude=PATTERN      exclude certain file patterns from the compilation
        # * parallel=N    run builds in N parallel jobs (default: calculated per system)
        exclude = "**.py"
        parallel = 12

        [tool.local.cythonize.kwargs.directives]
        # This section can contain compiler directives
        # NAME = "VALUE"

        [tool.local.cythonize.kwargs.compile-time-env]
        # This section can contain compile time env vars
        # NAME = "VALUE"

        [tool.local.cythonize.kwargs.options]
        # This section can contain cythonize options
        # NAME = "VALUE"
    """
    cwd_path = os.path.realpath(os.getcwd())
    with open(os.path.join(cwd_path, 'pyproject.toml')) as config_file:
        return toml.load(config_file)['tool']['local']['cythonize']


@contextlib.contextmanager
def patched_distutils_cmd_install():
    """Make `install_lib` of `install` cmd always use `platlib`.

    :yields: None
    """
    # Without this, build_lib puts stuff under `*.data/purelib/` folder
    orig_finalize = distutils_install_cmd.finalize_options

    def new_finalize_options(self):  # noqa: WPS430
        self.install_lib = self.install_platlib
        orig_finalize(self)

    distutils_install_cmd.finalize_options = new_finalize_options
    try:  # noqa: WPS501
        yield
    finally:
        distutils_install_cmd.finalize_options = orig_finalize


@contextlib.contextmanager
def patched_dist_has_ext_modules():
    """Make `has_ext_modules` of `Distribution` always return `True`.

    :yields: None
    """
    # Without this, build_lib puts stuff under `*.data/platlib/` folder
    orig_func = distutils_distribution.has_ext_modules

    distutils_distribution.has_ext_modules = lambda *args, **kwargs: True
    try:  # noqa: WPS501
        yield
    finally:
        distutils_distribution.has_ext_modules = orig_func


@contextlib.contextmanager
def patched_env(env):
    """Temporary set given env vars.

    :param env: tmp env vars to set
    :type env: dict

    :yields: None
    """
    orig_env = os.environ.copy()
    expanded_env = {name: expandvars(var_val) for name, var_val in env.items()}
    os.environ.update(expanded_env)
    if os.getenv('ANSIBLE_PYLIBSSH_TRACING') == '1':
        os.environ['CFLAGS'] = ' '.join((
            os.getenv('CFLAGS', ''),
            '-DCYTHON_TRACE=1',
            '-DCYTHON_TRACE_NOGIL=1',
        )).strip()
    try:  # noqa: WPS501
        yield
    finally:
        os.environ.clear()
        os.environ.update(orig_env)


def _emit_opt_pairs(opt_pair):
    flag, flag_value = opt_pair
    flag_opt = '--{name!s}'.format(name=flag)
    if isinstance(flag_value, dict):
        sub_pairs = flag_value.items()
    else:
        sub_pairs = ((flag_value, ), )

    for pair in sub_pairs:  # noqa: WPS526
        yield '='.join(map(str, (flag_opt, ) + pair))


def pre_build_cython(orig_func):  # noqa: WPS210
    """Pre-build cython exts before invoking ``orig_func``.

    :param orig_func: function being wrapped
    :type orig_func: callable

    :returns: function wrapper
    :rtype: callable
    """
    @functools.wraps(orig_func)  # noqa: WPS210, WPS430
    def func_wrapper(*args, **kwargs):  # noqa: WPS210, WPS430
        config = get_config()

        py_ver_arg = '-{maj_ver!s}'.format(maj_ver=sys.version_info.major)
        cli_flags = [
            '--{flag}'.format(flag=flag)
            for flag, is_enabled in config['flags'].items()
            if is_enabled
        ]

        cli_kwargs = list(chain.from_iterable(
            map(_emit_opt_pairs, config['kwargs'].items()),
        ))
        cythonize_args = cli_flags + [py_ver_arg] + cli_kwargs + config['src']
        if sys.version_info[0] == 2:  # cythonize wants str() internally
            # turn Unicode into native Python 2 `str`:
            cythonize_args = [arg.encode() for arg in cythonize_args]
        with patched_env(config['env']):
            cythonize_cli_cmd(cythonize_args)
        with patched_distutils_cmd_install():
            with patched_dist_has_ext_modules():
                return orig_func(*args, **kwargs)
    return func_wrapper


build_wheel = pre_build_cython(build_wheel)  # pylint: disable=invalid-name
