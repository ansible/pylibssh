# -*- coding: utf-8 -*-

"""PEP 517 build backend pre-building Cython exts before setuptools."""

# from __future__ import annotations

import os
import typing as t  # noqa: WPS111
from contextlib import contextmanager, suppress
from pathlib import Path
from shutil import copytree, ignore_patterns
from sys import version_info as _python_version_tuple
from tempfile import TemporaryDirectory

from setuptools.build_meta import (  # noqa: F401
    build_sdist as _setuptools_build_sdist,
)
from setuptools.build_meta import (  # noqa: F401
    build_wheel as _setuptools_build_wheel,
)
from setuptools.build_meta import (
    get_requires_for_build_wheel as _setuptools_get_requires_for_build_wheel,
)
from setuptools.build_meta import (
    prepare_metadata_for_build_wheel as _setuptools_prepare_metadata_for_build_wheel,
)


try:
    from setuptools.build_meta import (  # noqa: WPS433
        build_editable as _setuptools_build_editable,
    )
except ImportError:
    _setuptools_build_editable = None  # noqa: WPS440


# isort: split
from distutils.command.install import install as _distutils_install_cmd
from distutils.core import Distribution as _DistutilsDistribution
from distutils.dist import (
    DistributionMetadata as _DistutilsDistributionMetadata,
)


with suppress(ImportError):
    # NOTE: Only available for wheel builds that bundle C-extensions. Declared
    # NOTE: by `get_requires_for_build_wheel()` and
    # NOTE: `get_requires_for_build_editable()`, when `pure-python`
    # NOTE: is not passed.
    from Cython.Build.Cythonize import (  # noqa: WPS433
        main as _cythonize_cli_cmd,
    )

from ._compat import chdir_cm, nullcontext_cm  # noqa: WPS436
from ._cython_configuration import (  # noqa: WPS436
    get_local_cython_config as _get_local_cython_config,
)
from ._cython_configuration import (  # noqa: WPS436
    make_cythonize_cli_args_from_config as _make_cythonize_cli_args_from_config,
)
from ._cython_configuration import (  # noqa: WPS436
    patched_env as _patched_cython_env,
)
from ._transformers import sanitize_rst_roles  # noqa: WPS436


__all__ = (  # noqa: WPS410
    'build_sdist',
    'build_wheel',
    'get_requires_for_build_wheel',
    'prepare_metadata_for_build_wheel',
    *(
        () if _setuptools_build_editable is None
        else (
            'build_editable',
            'get_requires_for_build_editable',
            'prepare_metadata_for_build_editable',
        )
    ),
)


CYTHON_TRACING_CONFIG_SETTING = 'with-cython-tracing'  # noqa: WPS462
"""
Config setting name toggle to include line tracing to C-exts.
"""  # noqa: WPS322, WPS428

CYTHON_TRACING_ENV_VAR = 'ANSIBLE_PYLIBSSH_CYTHON_TRACING'  # noqa: WPS462
"""
Environment variable name toggle used to opt out of making C-exts.
"""  # noqa: WPS322, WPS428

IS_PY3_12_PLUS = _python_version_tuple[:2] >= (3, 12)  # noqa: WPS462
"""
A flag meaning that the current runtime is Python 3.12 or higher.
"""  # noqa: WPS322 WPS428


def _is_truthy_setting_value(setting_value: str) -> bool:
    truthy_values = {'', None, 'true', '1', 'on'}
    return setting_value.lower() in truthy_values


def _get_setting_value(
        config_settings: 'dict[str, str] | None' = None,  # noqa: WPS318
        config_setting_name: 'str | None' = None,
        env_var_name: 'str | None' = None,
        *,
        default: bool = False,
) -> bool:
    user_provided_setting_sources = (  # noqa: WPS317
        (config_settings, config_setting_name, (KeyError, TypeError)),
        (os.environ, env_var_name, KeyError),
    )
    for src_mapping, src_key, lookup_errors in user_provided_setting_sources:
        if src_key is None:
            continue

        with suppress(lookup_errors):  # type: ignore[arg-type]
            return _is_truthy_setting_value(src_mapping[src_key])  # type: ignore[index]

    return default


def _include_cython_line_tracing(
        config_settings: 'dict[str, str] | None' = None,  # noqa: WPS318
        *,
        default=False,
) -> bool:
    return _get_setting_value(
        config_settings,
        CYTHON_TRACING_CONFIG_SETTING,
        CYTHON_TRACING_ENV_VAR,
        default=default,
    )


@contextmanager
def patched_distutils_cmd_install():
    """Make `install_lib` of `install` cmd always use `platlib`.

    :yields: None
    """
    # Without this, build_lib puts stuff under `*.data/purelib/` folder
    orig_finalize = _distutils_install_cmd.finalize_options

    def new_finalize_options(self):  # noqa: WPS430
        self.install_lib = self.install_platlib
        orig_finalize(self)

    _distutils_install_cmd.finalize_options = new_finalize_options
    try:  # noqa: WPS501
        yield
    finally:
        _distutils_install_cmd.finalize_options = orig_finalize


@contextmanager
def patched_dist_has_ext_modules():
    """Make `has_ext_modules` of `Distribution` always return `True`.

    :yields: None
    """
    # Without this, build_lib puts stuff under `*.data/platlib/` folder
    orig_func = _DistutilsDistribution.has_ext_modules

    _DistutilsDistribution.has_ext_modules = lambda *args, **kwargs: True
    try:  # noqa: WPS501
        yield
    finally:
        _DistutilsDistribution.has_ext_modules = orig_func


@contextmanager
def patched_dist_get_long_description():
    """Make `has_ext_modules` of `Distribution` always return `True`.

    :yields: None
    """
    # Without this, build_lib puts stuff under `*.data/platlib/` folder
    orig_func = _DistutilsDistributionMetadata.get_long_description

    def _get_sanitized_long_description(self):  # noqa: WPS430
        return sanitize_rst_roles(self.long_description)

    _DistutilsDistributionMetadata.get_long_description = (
        _get_sanitized_long_description
    )
    try:
        yield
    finally:
        _DistutilsDistributionMetadata.get_long_description = orig_func


@contextmanager
def _in_temporary_directory(src_dir: Path) -> t.Iterator[None]:
    with TemporaryDirectory(prefix='.tmp-ansible-pylibssh-pep517-') as tmp_dir:
        # Make sure we do not copy src_dir into src_dir, that would create
        # infinite recursion. This happens during rpmbuild were TMPDIR
        # environment variable is set to src_dir/.pyproject-build.
        ignore = ignore_patterns(Path(tmp_dir).name)
        with chdir_cm(tmp_dir):
            tmp_src_dir = Path(tmp_dir) / 'src'
            copytree(src_dir, tmp_src_dir, symlinks=True, ignore=ignore)
            os.chdir(tmp_src_dir)
            yield


@contextmanager
def _prebuild_c_extensions(
        line_trace_cython_when_unset: bool = False,  # noqa: WPS318
        build_inplace: bool = False,
        config_settings: 'dict[str, str] | None' = None,
) -> t.Generator[None, t.Any, t.Any]:
    """Pre-build C-extensions in a temporary directory, when needed.

    This context manager also patches metadata, setuptools and distutils.

    :param build_inplace: Whether to copy and chdir to a temporary location.
    :param config_settings: :pep:`517` config settings mapping.

    """
    cython_line_tracing_requested = _include_cython_line_tracing(
        config_settings,
        default=line_trace_cython_when_unset,
    )

    build_dir_ctx = (
        nullcontext_cm() if build_inplace
        else _in_temporary_directory(src_dir=Path.cwd().resolve())
    )
    with build_dir_ctx:
        config = _get_local_cython_config()

        cythonize_args = _make_cythonize_cli_args_from_config(config)
        with _patched_cython_env(config['env'], cython_line_tracing_requested):
            _cythonize_cli_cmd(cythonize_args)
        with patched_distutils_cmd_install():
            with patched_dist_has_ext_modules():
                yield


@patched_dist_get_long_description()
def build_wheel(
        wheel_directory: str,  # noqa: WPS318
        config_settings: 'dict[str, str] | None' = None,
        metadata_directory: 'str | None' = None,
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


@patched_dist_get_long_description()
def build_editable(
        wheel_directory: str,  # noqa: WPS318
        config_settings: 'dict[str, str] | None' = None,
        metadata_directory: 'str | None' = None,
) -> str:
    """Produce a built wheel for editable installs.

    This wraps the corresponding ``setuptools``' build backend hook.

    :param wheel_directory: Directory to put the resulting wheel in.
    :param config_settings: :pep:`517` config settings mapping.
    :param metadata_directory: :file:`.dist-info` directory path.

    """
    with _prebuild_c_extensions(
            line_trace_cython_when_unset=True,  # noqa: WPS318
            build_inplace=True,
            config_settings=config_settings,
    ):
        return _setuptools_build_editable(
            wheel_directory=wheel_directory,
            config_settings=config_settings,
            metadata_directory=metadata_directory,
        )


def get_requires_for_build_wheel(
        config_settings: 'dict[str, str] | None' = None,  # noqa: WPS318
) -> 'list[str]':
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


build_sdist = patched_dist_get_long_description()(_setuptools_build_sdist)
get_requires_for_build_editable = get_requires_for_build_wheel
prepare_metadata_for_build_wheel = patched_dist_get_long_description()(
    _setuptools_prepare_metadata_for_build_wheel,
)
prepare_metadata_for_build_editable = prepare_metadata_for_build_wheel
