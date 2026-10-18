"""PEP 517 build backend wrapper for pre-building Cython for wheel."""

from __future__ import annotations

import os
import shlex
import sysconfig
import typing as _t
from contextlib import contextmanager, nullcontext, suppress
from functools import partial
from importlib.metadata import (
    PackageNotFoundError,
    version as _dist_version,
)
from pathlib import Path
from shutil import copytree
from sys import (
    implementation as _system_implementation,
    platform as _system_platform,
    stderr as _standard_error_stream,
)
from tempfile import TemporaryDirectory

from setuptools.build_meta import (  # noqa: F401
    build_sdist as _setuptools_build_sdist,
    build_wheel as _setuptools_build_wheel,
    get_requires_for_build_wheel as _setuptools_get_requires_for_build_wheel,
    prepare_metadata_for_build_wheel as _setuptools_prepare_metadata_for_build_wheel,
)


try:
    from setuptools.build_meta import (
        build_editable as _setuptools_build_editable,
    )
except ImportError:
    _setuptools_build_editable = None  # type: ignore[assignment]


# isort: split
from distutils.command.install import install as _distutils_install_cmd
from distutils.dist import (
    Distribution as _DistutilsDistribution,
    DistributionMetadata as _DistutilsDistributionMetadata,
)


with suppress(ImportError):
    # NOTE: Only available for wheel builds that bundle C-extensions. Declared
    # NOTE: by `get_requires_for_build_wheel()` and
    # NOTE: `get_requires_for_build_editable()`, when `pure-python`
    # NOTE: is not passed.
    from Cython.Build.Cythonize import (
        main as _cythonize_cli_cmd,
    )

from ._compat import chdir_cm
from ._compat_setup_cfg import compat_setup_cfg_written
from ._cython_configuration import (
    get_local_cythonize_config as _get_local_cython_config,
    get_local_min_python_version as _get_local_min_python_version,
    make_cythonize_cli_args_from_config as _make_cythonize_cli_args_from_config,
    patched_env as _patched_cython_env,
)
from ._transformers import sanitize_rst_roles


if _t.TYPE_CHECKING:
    from collections import abc as _c

    from typing_extensions import TypeAlias


__all__ = (  # noqa: PLE0604, WPS410
    'build_sdist',
    'build_wheel',
    'get_requires_for_build_wheel',
    'prepare_metadata_for_build_wheel',
    *(
        ()
        if _setuptools_build_editable is None
        else (
            'build_editable',
            'get_requires_for_build_editable',
            'prepare_metadata_for_build_editable',
        )
    ),
)


_ConfigDict: TypeAlias = 'dict[str, str | list[str] | None]'


CYTHON_TRACING_CONFIG_SETTING = 'with-cython-tracing'  # noqa: WPS462
"""
Config setting name toggle to include line tracing to C-exts.
"""  # noqa: WPS322

CYTHON_TRACING_ENV_VAR = 'ANSIBLE_PYLIBSSH_CYTHON_TRACING'  # noqa: WPS462
"""
Environment variable name toggle used to opt out of making C-exts.
"""  # noqa: WPS322

IS_CPYTHON = _system_implementation.name == 'cpython'
"""A flag meaning that the current interpreter implementation is CPython."""

CYTHON_LIMITED_API_MIN_VERSION = 3, 1
"""The oldest Cython that targets the limited C API with ``Py_LIMITED_API``."""


def _get_cython_version() -> tuple[int, int]:
    try:
        cython_version = _dist_version('Cython')
    except PackageNotFoundError:
        return 0, 0
    major, minor = cython_version.split('.')[:2]
    return int(major), int(minor)


def can_build_for_limited_api(*, cython_line_tracing_requested: bool) -> bool:
    """Check if the C-extensions can be built for the stable ABI (abi3).

    :param cython_line_tracing_requested: Whether Cython line tracing is on.
    :returns: Whether the limited C API can be used for the build.
    """
    if cython_line_tracing_requested:
        # Cython cannot trace lines under the limited C API:
        return False

    return (
        IS_CPYTHON
        # `Python.h` refuses `Py_LIMITED_API` on free-threaded CPython:
        and not sysconfig.get_config_var('Py_GIL_DISABLED')
        # MSVC does not read `CPPFLAGS` that carries `Py_LIMITED_API`:
        and _system_platform != 'win32'
        # Older Cython generates code for the full C API regardless:
        and _get_cython_version() >= CYTHON_LIMITED_API_MIN_VERSION
    )


def with_limited_api_wheel_tag(
    config_settings: _ConfigDict | None,
    *,
    limited_api_version: tuple[int, int],
) -> _ConfigDict:
    """Make ``bdist_wheel`` tag the wheel as a stable ABI (abi3) one.

    :param config_settings: :pep:`517` config settings mapping.
    :param limited_api_version: The oldest CPython the wheel works under.
    :returns: A copy of the config settings with the extra build option.
    """
    config_settings = dict(config_settings or {})
    build_options = config_settings.get('--build-option') or []
    if isinstance(build_options, str):
        build_options = shlex.split(build_options)
    major, minor = limited_api_version
    config_settings['--build-option'] = [
        *build_options,
        f'--py-limited-api=cp{major}{minor}',
    ]
    return config_settings


def _is_truthy_setting_value(setting_value: str) -> bool:
    truthy_values = {'', None, 'true', '1', 'on'}
    return setting_value.lower() in truthy_values


def _get_setting_value(
    config_settings: _ConfigDict | None = None,
    config_setting_name: str | None = None,
    env_var_name: str | None = None,
    *,
    default: bool = False,
) -> bool:
    user_provided_setting_sources = (
        (config_settings, config_setting_name, (KeyError, TypeError)),
        (os.environ, env_var_name, KeyError),
    )
    for src_mapping, src_key, lookup_errors in user_provided_setting_sources:
        if src_key is None:
            continue

        with suppress(lookup_errors):  # type: ignore[arg-type]
            return _is_truthy_setting_value(src_mapping[src_key])  # type: ignore[arg-type,index,unused-ignore]

    return default


def _include_cython_line_tracing(
    config_settings: _ConfigDict | None = None,
    *,
    default: bool = False,
) -> bool:
    return _get_setting_value(
        config_settings,
        CYTHON_TRACING_CONFIG_SETTING,
        CYTHON_TRACING_ENV_VAR,
        default=default,
    )


@contextmanager
def patched_distutils_cmd_install() -> _c.Iterator[None]:
    """Make `install_lib` of `install` cmd always use `platlib`.

    :yields: None
    """
    # Without this, build_lib puts stuff under `*.data/purelib/` folder
    orig_finalize = _distutils_install_cmd.finalize_options

    def new_finalize_options(  # noqa: WPS430
        self: _distutils_install_cmd,
    ) -> None:
        self.install_lib = self.install_platlib
        orig_finalize(self)

    _distutils_install_cmd.finalize_options = new_finalize_options  # type: ignore[method-assign]
    try:  # noqa: WPS501
        yield
    finally:
        _distutils_install_cmd.finalize_options = orig_finalize  # type: ignore[method-assign]


@contextmanager
def patched_dist_has_ext_modules() -> _c.Iterator[None]:
    """Make `has_ext_modules` of `Distribution` always return `True`.

    :yields: None
    """
    # Without this, build_lib puts stuff under `*.data/platlib/` folder
    orig_func = _DistutilsDistribution.has_ext_modules

    _DistutilsDistribution.has_ext_modules = lambda *_args, **_kwargs: True  # type: ignore[method-assign]
    try:  # noqa: WPS501
        yield
    finally:
        _DistutilsDistribution.has_ext_modules = orig_func  # type: ignore[method-assign]


@contextmanager
def patched_dist_get_long_description() -> _c.Iterator[None]:
    """Make `has_ext_modules` of `Distribution` always return `True`.

    :yields: None
    """
    # Without this, build_lib puts stuff under `*.data/platlib/` folder
    orig_func = _DistutilsDistributionMetadata.get_long_description

    def _get_sanitized_long_description(  # noqa: WPS430
        self: _DistutilsDistributionMetadata,
    ) -> str:
        assert self.long_description is not None  # noqa: S101  # typing
        return sanitize_rst_roles(self.long_description)

    _DistutilsDistributionMetadata.get_long_description = (  # type: ignore[method-assign]
        _get_sanitized_long_description
    )
    try:
        yield
    finally:
        _DistutilsDistributionMetadata.get_long_description = orig_func  # type: ignore[method-assign]


def _exclude_dir_path(
    excluded_dir_path: Path,
    visited_directory: str,
    _visited_dir_contents: list[str],
) -> list[str]:
    """Prevent recursive directory traversal."""
    # This stops the temporary directory from being copied
    # into self recursively forever.
    # Ref: https://github.com/aio-libs/yarl/issues/992
    visited_directory_subdirs_to_ignore = [
        subdir
        for subdir in _visited_dir_contents
        if excluded_dir_path == Path(visited_directory) / subdir
    ]
    if visited_directory_subdirs_to_ignore:
        print(  # noqa: T201, WPS421
            f'Preventing `{excluded_dir_path!s}` from being '
            'copied into itself recursively...',
            file=_standard_error_stream,
        )
    return visited_directory_subdirs_to_ignore


@contextmanager
def _in_temporary_directory(src_dir: Path) -> _c.Iterator[None]:
    with TemporaryDirectory(prefix='.tmp-ansible-pylibssh-pep517-') as tmp_dir:
        tmp_dir_path = Path(tmp_dir)
        root_tmp_dir_path = tmp_dir_path.parent
        exclude_tmpdir_parent = partial(_exclude_dir_path, root_tmp_dir_path)

        with chdir_cm(tmp_dir):
            tmp_src_dir = tmp_dir_path / 'src'
            copytree(
                src_dir,
                tmp_src_dir,
                ignore=exclude_tmpdir_parent,
                symlinks=True,
            )
            os.chdir(tmp_src_dir)
            yield


@contextmanager
def _prebuild_c_extensions(
    *,
    line_trace_cython_when_unset: bool = False,
    build_inplace: bool = False,
    config_settings: _ConfigDict | None = None,
) -> _c.Iterator[tuple[int, int] | None]:
    """Pre-build C-extensions in a temporary directory, when needed.

    This context manager also patches metadata, setuptools and distutils.

    :param build_inplace: Whether to copy and chdir to a temporary location.
    :param config_settings: :pep:`517` config settings mapping.
    :yields: The oldest CPython that the C-extensions were built for the
        stable ABI (abi3) of, if they were.

    """
    cython_line_tracing_requested = _include_cython_line_tracing(
        config_settings,
        default=line_trace_cython_when_unset,
    )

    build_dir_ctx = (
        nullcontext()
        if build_inplace
        else _in_temporary_directory(src_dir=Path.cwd().resolve())
    )
    with build_dir_ctx:
        config = _get_local_cython_config()
        limited_api_version = (
            _get_local_min_python_version()
            if can_build_for_limited_api(
                cython_line_tracing_requested=cython_line_tracing_requested,
            )
            else None
        )

        cythonize_args = _make_cythonize_cli_args_from_config(
            config,
        )
        with _patched_cython_env(
            config['env'],
            cython_line_tracing_requested=cython_line_tracing_requested,
            limited_api_version=limited_api_version,
        ):
            _cythonize_cli_cmd(cythonize_args)  # type: ignore[no-untyped-call]
        with patched_distutils_cmd_install():
            with patched_dist_has_ext_modules():
                yield limited_api_version


@patched_dist_get_long_description()
def build_wheel(
    wheel_directory: str,
    config_settings: _ConfigDict | None = None,
    metadata_directory: str | None = None,
) -> str:
    """Produce a built wheel.

    This wraps the corresponding ``setuptools``' build backend hook.

    :param wheel_directory: Directory to put the resulting wheel in.
    :param config_settings: :pep:`517` config settings mapping.
    :param metadata_directory: :file:`.dist-info` directory path.

    """
    with _prebuild_c_extensions(
        line_trace_cython_when_unset=False,
        build_inplace=False,
        config_settings=config_settings,
    ) as limited_api_version:
        return _setuptools_build_wheel(
            wheel_directory=wheel_directory,
            config_settings=(
                config_settings
                if limited_api_version is None
                else with_limited_api_wheel_tag(
                    config_settings,
                    limited_api_version=limited_api_version,
                )
            ),
            metadata_directory=metadata_directory,
        )


@patched_dist_get_long_description()
def build_editable(
    wheel_directory: str,
    config_settings: _ConfigDict | None = None,
    metadata_directory: str | None = None,
) -> str:
    """Produce a built wheel for editable installs.

    This wraps the corresponding ``setuptools``' build backend hook.

    :param wheel_directory: Directory to put the resulting wheel in.
    :param config_settings: :pep:`517` config settings mapping.
    :param metadata_directory: :file:`.dist-info` directory path.

    """
    with _prebuild_c_extensions(
        line_trace_cython_when_unset=True,
        build_inplace=True,
        config_settings=config_settings,
    ):
        return _setuptools_build_editable(
            wheel_directory=wheel_directory,
            config_settings=config_settings,
            metadata_directory=metadata_directory,
        )


def get_requires_for_build_wheel(
    config_settings: _ConfigDict | None = None,
) -> list[str]:
    """Determine additional requirements for building wheels.

    :param config_settings: :pep:`517` config settings mapping.

    """
    c_ext_build_deps = [
        'Cython >= 3.0.11; python_version >= "3.13"',  # Ideally >= 3.1.0
        'Cython >= 3.0.0; python_version >= "3.12" and python_version < "3.13"',
        'Cython; python_version < "3.12"',
    ]

    return (
        _setuptools_get_requires_for_build_wheel(
            config_settings=config_settings,
        )
        + c_ext_build_deps
    )


@patched_dist_get_long_description()
def build_sdist(
    sdist_directory: str,
    config_settings: _ConfigDict | None = None,
) -> str:
    """Produce an sdist, shipping a compat ``setup.cfg`` in it.

    This wraps the corresponding ``setuptools``' build backend hook.

    :param sdist_directory: Directory to put the resulting sdist in.
    :param config_settings: :pep:`517` config settings mapping.

    """
    with compat_setup_cfg_written(Path.cwd()):
        return _setuptools_build_sdist(
            sdist_directory=sdist_directory,
            config_settings=config_settings,
        )


get_requires_for_build_editable = get_requires_for_build_wheel
prepare_metadata_for_build_wheel = patched_dist_get_long_description()(
    _setuptools_prepare_metadata_for_build_wheel,
)
prepare_metadata_for_build_editable = prepare_metadata_for_build_wheel
