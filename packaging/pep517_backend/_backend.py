# -*- coding: utf-8 -*-

"""PEP 517 build backend pre-building Cython exts before setuptools."""

from __future__ import annotations

import os
import typing as t  # noqa: WPS111
from contextlib import contextmanager, nullcontext, suppress
from sys import version_info as _python_version_tuple

from setuptools.build_meta import (  # noqa: F401  # Re-exporting PEP 517 hooks
    build_wheel as _setuptools_build_wheel,
)
from setuptools.build_meta import (
    get_requires_for_build_wheel as _setuptools_get_requires_for_build_wheel,
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


with suppress(ImportError):
    # NOTE: Only available for wheel builds that bundle C-extensions. Declared
    # NOTE: by `get_requires_for_build_wheel()` and
    # NOTE: `get_requires_for_build_editable()`, when `pure-python`
    # NOTE: is not passed.
    from Cython.Build.Cythonize import (  # noqa: WPS433
        main as _cythonize_cli_cmd,
    )

from ._cython_configuration import (  # noqa: WPS436
    get_local_cython_config as _get_local_cython_config,
)
from ._cython_configuration import (  # noqa: WPS436
    make_cythonize_cli_args_from_config as _make_cythonize_cli_args_from_config,
)
from ._cython_configuration import (  # noqa: WPS436
    patched_env as _patched_cython_env,
)
from ._transformers import convert_to_kwargs_only  # noqa: WPS436


IS_PY3_12_PLUS = _python_version_tuple[:2] >= (3, 12)  # noqa: WPS462
"""
A flag meaning that the current runtime is Python 3.12 or higher.
"""  # noqa: WPS322 WPS428


@contextmanager
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


@contextmanager
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


@contextmanager
def _prebuild_c_extensions(
        line_trace_cython_when_unset: bool = False,  # noqa: WPS318
        build_inplace: bool = False,
        config_settings: dict[str, str] | None = None,
) -> t.Generator[None, t.Any, t.Any]:
    """Pre-build C-extensions in a temporary directory, when needed.

    This context manager also patches metadata, setuptools and distutils.

    :param build_inplace: Whether to copy and chdir to a temporary location.
    :param config_settings: :pep:`517` config settings mapping.

    """
    cython_line_tracing_requested = os.getenv(
        'ANSIBLE_PYLIBSSH_TRACING',
        line_trace_cython_when_unset,
    ) == '1'

    build_dir_ctx = nullcontext()
    with build_dir_ctx:
        config = _get_local_cython_config()

        cythonize_args = _make_cythonize_cli_args_from_config(config)
        with _patched_cython_env(config['env'], cython_line_tracing_requested):
            _cythonize_cli_cmd(cythonize_args)
        with patched_distutils_cmd_install():
            with patched_dist_has_ext_modules():
                yield


@convert_to_kwargs_only
def build_wheel(
        wheel_directory: str,  # noqa: WPS318
        config_settings: dict[str, str] | None = None,
        metadata_directory: str | None = None,
) -> str:
    """Produce a built wheel.

    This wraps the corresponding ``setuptools``' build backend hook.

    :param wheel_directory: Directory to put the resulting wheel in.
    :param config_settings: :pep:`517` config settings mapping.
    :param metadata_directory: :file:`.dist-info` directory path.

    """
    with _prebuild_c_extensions(
            line_trace_cython_when_unset=False,  # noqa: WPS318
            build_inplace=False,
            config_settings=config_settings,
    ):
        return _setuptools_build_wheel(
            wheel_directory=wheel_directory,
            config_settings=config_settings,
            metadata_directory=metadata_directory,
        )


def get_requires_for_build_wheel(
        config_settings: dict[str, str] | None = None,  # noqa: WPS318
) -> list[str]:
    """Determine additional requirements for building wheels.

    :param config_settings: :pep:`517` config settings mapping.

    """
    c_ext_build_deps = [
        'Cython >= 3.0.0b3' if IS_PY3_12_PLUS  # Only Cython 3+ is compatible
        else 'Cython',
    ]

    return _setuptools_get_requires_for_build_wheel(
        config_settings=config_settings,
    ) + c_ext_build_deps


if _setuptools_build_editable is not None:
    build_editable = build_wheel
    get_requires_for_build_editable = get_requires_for_build_wheel
