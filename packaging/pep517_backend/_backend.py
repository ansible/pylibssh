# -*- coding: utf-8 -*-

"""PEP 517 build backend pre-building Cython exts before setuptools."""

import contextlib
import os
import sys
from functools import wraps
from pathlib import Path

from expandvars import expandvars
from setuptools.build_meta import (  # noqa: F401  # Re-exporting PEP 517 hooks
    build_wheel,
)


try:
    from setuptools.build_meta import (  # noqa: WPS433
        build_editable as _setuptools_build_editable,
    )
except ImportError:
    _setuptools_build_editable = None  # noqa: WPS440


# isort: split
from distutils.command.install import install as distutils_install_cmd
from distutils.core import Distribution as DistutilsDistribution

from Cython.Build.Cythonize import main as cythonize_cli_cmd

from ._compat import load_toml_from_string  # noqa: WPS436
from ._transformers import (  # noqa: WPS436
    convert_to_kwargs_only, get_cli_kwargs_from_config,
    get_enabled_cli_flags_from_config,
)


PROJECT_ROOT_DIR = Path(__file__).parents[2].resolve()
PYPROJECT_TOML_PATH = PROJECT_ROOT_DIR / 'pyproject.toml'


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
    config_file = PYPROJECT_TOML_PATH.read_text(encoding='utf-8')
    config_toml = load_toml_from_string(config_file)
    return config_toml['tool']['local']['cythonize']


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
    orig_func = DistutilsDistribution.has_ext_modules

    DistutilsDistribution.has_ext_modules = lambda *args, **kwargs: True
    try:  # noqa: WPS501
        yield
    finally:
        DistutilsDistribution.has_ext_modules = orig_func


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


def pre_build_cython(orig_func):  # noqa: WPS210
    """Pre-build cython exts before invoking ``orig_func``.

    :param orig_func: function being wrapped
    :type orig_func: callable

    :returns: function wrapper
    :rtype: callable
    """
    @wraps(orig_func)
    def func_wrapper(*args, **kwargs):  # noqa: WPS210, WPS430
        config = get_config()

        py_ver_arg = '-{maj_ver!s}'.format(maj_ver=sys.version_info.major)

        cli_flags = get_enabled_cli_flags_from_config(config['flags'])
        cli_kwargs = get_cli_kwargs_from_config(config['kwargs'])

        cythonize_args = cli_flags + [py_ver_arg] + cli_kwargs + config['src']
        with patched_env(config['env']):
            cythonize_cli_cmd(cythonize_args)
        with patched_distutils_cmd_install():
            with patched_dist_has_ext_modules():
                return orig_func(**kwargs)
    return func_wrapper


build_wheel = convert_to_kwargs_only(  # pylint: disable=invalid-name
    pre_build_cython(build_wheel),
)

if _setuptools_build_editable is not None:
    build_editable = build_wheel
