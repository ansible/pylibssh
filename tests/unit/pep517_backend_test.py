"""Tests for the in-tree PEP 517 build backend."""

from __future__ import annotations

import configparser
import os
import pathlib
import shlex
import sysconfig
import types as _tps
import typing as _t

import pytest

from pep517_backend._compat import chdir_cm, load_toml_from_string
from pep517_backend._compat_setup_cfg import (
    compat_setup_cfg_written,
    render_compat_setup_cfg,
)
from pep517_backend._cython_configuration import (
    get_abi3_extension_suffix,
    get_local_min_python_version,
    patched_env,
)


CFLAGS_VAR = 'CFLAGS'
CPPFLAGS_VAR = 'CPPFLAGS'
EXT_SUFFIX_VAR = 'SETUPTOOLS_EXT_SUFFIX'
TRACE_MACRO = '-DCYTHON_TRACE_NOGIL=1'
SYS_MONITORING_MACRO = '-DCYTHON_USE_SYS_MONITORING=0'
LIMITED_API_MACRO = '-DPy_LIMITED_API=0x03090000'
LIMITED_API_BUILD_OPTION = '--py-limited-api=cp39'
BUILD_OPTION_SETTING = '--build-option'

PROJECT_ROOT_DIR = pathlib.Path(__file__).parents[2]
PYPROJECT_TOML_NAME = 'pyproject.toml'
SETUP_CFG_NAME = 'setup.cfg'
TEXT_ENCODING = 'utf-8'
METADATA_SECTION = 'metadata'
OPTIONS_SECTION = 'options'
README_KEY = 'readme'
PACKAGES_KEY = 'packages'
LICENSE_KEY = 'license'
SAMPLE_LICENSE = 'MIT'
MINIMAL_PYPROJECT_TOML = '[project]\nname = "pkg"\n'
NO_SETUPTOOLS_CONFIG: _t.Mapping[str, _t.Any] = _tps.MappingProxyType({})
NAME_KEY = 'name'
RST_README_CONFIG: _t.Mapping[str, _t.Any] = _tps.MappingProxyType(
    {
        'file': ['README.rst', 'CHANGES.rst'],
        'content-type': 'text/x-rst',
    },
)
UNTYPED_README_CONFIG: _t.Mapping[str, _t.Any] = _tps.MappingProxyType(
    {
        'file': ['README.rst'],
    },
)

# `setup.cfg` section and key, and the equivalent PEP 621 key:
EQUIVALENT_CORE_METADATA = (
    (METADATA_SECTION, NAME_KEY, NAME_KEY),
    (METADATA_SECTION, 'description', 'description'),
    (METADATA_SECTION, 'classifiers', 'classifiers'),
    (METADATA_SECTION, 'keywords', 'keywords'),
    (METADATA_SECTION, 'project_urls', 'urls'),
)


@pytest.mark.parametrize(
    'tracing',
    (True, False),
    ids=(
        'with-cython-tracing',
        'without-cython-tracing',
    ),
)
def test_tracing_macro_goes_through_cppflags(
    *,
    monkeypatch: pytest.MonkeyPatch,
    tracing: bool,
) -> None:
    """Append the macro to CPPFLAGS and leave CFLAGS alone.

    A CFLAGS environment variable replaces the interpreter's own compiler
    flags in setuptools' distutils, which silently drops -O3 from the
    build, while CPPFLAGS is appended to them.
    """
    monkeypatch.setenv(CFLAGS_VAR, '-fuser-cflag')
    monkeypatch.setenv(CPPFLAGS_VAR, '-DUSER=1')

    with patched_env({}, cython_line_tracing_requested=tracing):
        cppflags = shlex.split(os.environ[CPPFLAGS_VAR])
        assert os.environ[CFLAGS_VAR] == '-fuser-cflag'

    assert cppflags[0] == '-DUSER=1'
    assert (TRACE_MACRO in cppflags) is tracing
    assert (SYS_MONITORING_MACRO in cppflags) is tracing
    assert os.environ[CPPFLAGS_VAR] == '-DUSER=1'


@pytest.mark.skipif(
    os.name == 'nt',
    reason='MSVC does not read CFLAGS or CPPFLAGS',
)
def test_interpreter_flags_survive_the_build_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Keep the interpreter's flags and add the macro on top.

    This drives setuptools' real compiler customization, so it fails if the
    backend ever goes back to setting CFLAGS.
    """
    # A developer shell exporting these would replace the flags up front.
    monkeypatch.delenv(CFLAGS_VAR, raising=False)
    monkeypatch.delenv(CPPFLAGS_VAR, raising=False)
    # The RPM builds run the suite without setuptools available.
    ccompiler = pytest.importorskip('setuptools._distutils.ccompiler')
    distutils_sysconfig = pytest.importorskip(
        'setuptools._distutils.sysconfig',
    )
    interpreter_flags = shlex.split(sysconfig.get_config_var(CFLAGS_VAR) or '')

    pristine_compiler = ccompiler.new_compiler()
    distutils_sysconfig.customize_compiler(pristine_compiler)
    assert TRACE_MACRO not in pristine_compiler.compiler_so

    with patched_env({}, cython_line_tracing_requested=True):
        compiler = ccompiler.new_compiler()
        distutils_sysconfig.customize_compiler(compiler)
        command = compiler.compiler_so

    for flag in interpreter_flags:
        assert flag in command
    assert TRACE_MACRO in command
    assert SYS_MONITORING_MACRO in command


@pytest.fixture
def pep517_backend() -> _tps.ModuleType:
    """Import the build backend, which needs setuptools.

    :returns: The in-tree build backend module.
    """
    # The RPM builds run the suite without setuptools available.
    backend_module: _tps.ModuleType = pytest.importorskip(
        'pep517_backend._backend',
    )
    return backend_module


def test_limited_api_define_and_suffix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Define the stable ABI macro and name the modules after it.

    Both only last for the build, like the rest of the patched env.
    """
    monkeypatch.delenv(CPPFLAGS_VAR, raising=False)
    monkeypatch.delenv(EXT_SUFFIX_VAR, raising=False)

    with patched_env(
        {},
        cython_line_tracing_requested=False,
        limited_api_version=(3, 9),
    ):
        cppflags = shlex.split(os.environ[CPPFLAGS_VAR])
        ext_suffix = os.environ[EXT_SUFFIX_VAR]

    assert LIMITED_API_MACRO in cppflags
    assert ext_suffix == get_abi3_extension_suffix()
    assert EXT_SUFFIX_VAR not in os.environ


def test_version_specific_abi_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Target only the running interpreter without a limited API version."""
    monkeypatch.delenv(CPPFLAGS_VAR, raising=False)
    monkeypatch.delenv(EXT_SUFFIX_VAR, raising=False)

    with patched_env({}, cython_line_tracing_requested=False):
        cppflags = os.getenv(CPPFLAGS_VAR, '')
        has_ext_suffix = EXT_SUFFIX_VAR in os.environ

    assert 'Py_LIMITED_API' not in cppflags
    assert not has_ext_suffix


def test_abi3_extension_suffix() -> None:
    """Check that the suffix is the stable ABI one of this platform."""
    assert get_abi3_extension_suffix() in {'.abi3.so', '.pyd'}


def _set_up_build_env(
    monkeypatch: pytest.MonkeyPatch,
    pep517_backend: _tps.ModuleType,
    *,
    gil_disabled: int = 0,
    platform: str = 'linux',
    cython_version: tuple[int, int] = (3, 2),
) -> None:
    monkeypatch.setattr(pep517_backend, 'IS_CPYTHON', True)
    monkeypatch.setattr(pep517_backend, '_system_platform', platform)
    monkeypatch.setattr(
        pep517_backend,
        '_get_cython_version',
        lambda: cython_version,
    )
    monkeypatch.setattr(
        sysconfig,
        'get_config_var',
        {'Py_GIL_DISABLED': gil_disabled}.get,
    )


def test_can_build_for_limited_api(
    monkeypatch: pytest.MonkeyPatch,
    pep517_backend: _tps.ModuleType,
) -> None:
    """Use the stable ABI for release builds on regular CPython."""
    _set_up_build_env(monkeypatch, pep517_backend)

    assert pep517_backend.can_build_for_limited_api(
        cython_line_tracing_requested=False,
    )


@pytest.mark.parametrize(
    ('tracing', 'build_env'),
    (
        pytest.param(True, {}, id='tracing'),
        pytest.param(False, {'gil_disabled': 1}, id='free-threaded'),
        pytest.param(False, {'platform': 'win32'}, id='windows'),
        pytest.param(False, {'cython_version': (3, 0)}, id='cython-3.0'),
    ),
)
def test_cannot_build_for_limited_api(
    *,
    monkeypatch: pytest.MonkeyPatch,
    pep517_backend: _tps.ModuleType,
    tracing: bool,
    build_env: dict[str, _t.Any],
) -> None:
    """Skip the stable ABI where the build cannot actually target it."""
    _set_up_build_env(monkeypatch, pep517_backend, **build_env)

    assert not pep517_backend.can_build_for_limited_api(
        cython_line_tracing_requested=tracing,
    )


@pytest.mark.parametrize(
    ('cython_version', 'expected_version'),
    (
        pytest.param('3.2.4', (3, 2), id='release'),
        pytest.param('3.1.0rc1', (3, 1), id='pre-release'),
    ),
)
def test_cython_version(
    *,
    monkeypatch: pytest.MonkeyPatch,
    pep517_backend: _tps.ModuleType,
    cython_version: str,
    expected_version: tuple[int, int],
) -> None:
    """Read the major and minor version of the installed Cython."""
    monkeypatch.setattr(
        pep517_backend,
        '_dist_version',
        lambda _dist_name: cython_version,
    )

    assert pep517_backend._get_cython_version() == expected_version


def test_cython_version_without_cython(
    monkeypatch: pytest.MonkeyPatch,
    pep517_backend: _tps.ModuleType,
) -> None:
    """Treat a missing Cython as one too old for the limited C API."""
    look_up_dist_version = pep517_backend._dist_version
    monkeypatch.setattr(
        pep517_backend,
        '_dist_version',
        lambda _dist_name: look_up_dist_version('no-such-distribution'),
    )

    assert pep517_backend._get_cython_version() == (0, 0)


def _write_requires_python(
    project_dir: pathlib.Path,
    requires_python: str,
) -> None:
    (project_dir / PYPROJECT_TOML_NAME).write_text(
        f'[project]\nrequires-python = "{requires_python}"\n',
        encoding=TEXT_ENCODING,
    )


@pytest.mark.parametrize(
    ('requires_python', 'expected_version'),
    (
        pytest.param('>= 3.9', (3, 9), id='spaced'),
        pytest.param('>=3.10', (3, 10), id='compact'),
    ),
)
def test_local_min_python_version(
    tmp_path: pathlib.Path,
    requires_python: str,
    expected_version: tuple[int, int],
) -> None:
    """Get the oldest version out of the simple ``>= X.Y`` form."""
    _write_requires_python(tmp_path, requires_python)

    with chdir_cm(tmp_path):
        assert get_local_min_python_version() == expected_version


@pytest.mark.parametrize(
    'requires_python',
    (
        pytest.param('>= 3.9, < 4', id='upper-bound'),
        pytest.param('~= 3.9', id='compatible-release'),
        pytest.param('>= 3', id='major-only'),
    ),
)
def test_local_min_python_version_rejects(
    tmp_path: pathlib.Path,
    requires_python: str,
) -> None:
    """Refuse the forms that are not just a lower bound."""
    _write_requires_python(tmp_path, requires_python)

    with chdir_cm(tmp_path), pytest.raises(ValueError, match=r'>= X\.Y'):
        get_local_min_python_version()


def test_cannot_build_for_limited_api_off_cpython(
    monkeypatch: pytest.MonkeyPatch,
    pep517_backend: _tps.ModuleType,
) -> None:
    """Check that other runtimes have no CPython stable ABI to build for."""
    monkeypatch.setattr(pep517_backend, 'IS_CPYTHON', False)

    assert not pep517_backend.can_build_for_limited_api(
        cython_line_tracing_requested=False,
    )


@pytest.mark.parametrize(
    ('config_settings', 'expected_build_options'),
    (
        pytest.param(None, [LIMITED_API_BUILD_OPTION], id='no-settings'),
        pytest.param(
            {BUILD_OPTION_SETTING: '--foo --bar'},
            ['--foo', '--bar', LIMITED_API_BUILD_OPTION],
            id='string',
        ),
        pytest.param(
            {BUILD_OPTION_SETTING: ['--foo']},
            ['--foo', LIMITED_API_BUILD_OPTION],
            id='list',
        ),
    ),
)
def test_with_limited_api_wheel_tag(
    pep517_backend: _tps.ModuleType,
    config_settings: dict[str, str | list[str] | None] | None,
    expected_build_options: list[str],
) -> None:
    """Add the abi3 wheel tag option after any user build options."""
    new_settings = pep517_backend.with_limited_api_wheel_tag(
        config_settings,
        limited_api_version=(3, 9),
    )

    assert new_settings[BUILD_OPTION_SETTING] == expected_build_options
    assert new_settings is not config_settings


def _pyproject(
    setuptools_config: _t.Mapping[str, _t.Any] = NO_SETUPTOOLS_CONFIG,
    **project_settings: _t.Any,
) -> dict[str, _t.Any]:
    return {
        'project': {NAME_KEY: 'pkg', **project_settings},
        'tool': {'setuptools': dict(setuptools_config)},
    }


def _dynamic_readme_pyproject(
    readme_config: _t.Mapping[str, _t.Any],
    *,
    declared_dynamic: bool = True,
) -> dict[str, _t.Any]:
    project_settings = {'dynamic': [README_KEY]} if declared_dynamic else {}
    return _pyproject(
        {'dynamic': {README_KEY: dict(readme_config)}},
        **project_settings,
    )


def _render_and_parse(
    pyproject: _t.Mapping[str, _t.Any],
) -> configparser.ConfigParser:
    rendered_config = configparser.ConfigParser(interpolation=None)
    rendered_config.read_string(render_compat_setup_cfg(pyproject))
    return rendered_config


def _license_text(license_setting: _t.Any) -> str:
    # NOTE: The tree may carry the older PEP 621 license table, e.g. after
    # NOTE: the RPM spec rewrites it for setuptools predating PEP 639:
    if isinstance(license_setting, str):
        return license_setting
    return str(license_setting['text'])


def _normalize_specifier(specifier: object) -> str:
    return ''.join(str(specifier).split())


@pytest.mark.parametrize(
    ('pyproject', 'section', 'setting_name', 'expected_setting'),
    (
        pytest.param(
            _pyproject(),
            OPTIONS_SECTION,
            'include_package_data',
            'True',
            id='include-package-data-defaults-to-true',
        ),
        pytest.param(
            _pyproject({'include-package-data': False}),
            OPTIONS_SECTION,
            'include_package_data',
            'False',
            id='include-package-data-disabled',
        ),
        pytest.param(
            _pyproject(license=SAMPLE_LICENSE),
            METADATA_SECTION,
            LICENSE_KEY,
            SAMPLE_LICENSE,
            id='license-expression',
        ),
        pytest.param(
            _pyproject(license={'text': SAMPLE_LICENSE}),
            METADATA_SECTION,
            LICENSE_KEY,
            SAMPLE_LICENSE,
            id='license-text-table',
        ),
        pytest.param(
            _pyproject(urls={'Source': 'https://e.g'}),
            METADATA_SECTION,
            'project_urls',
            '\nSource = https://e.g',
            id='urls',
        ),
        pytest.param(
            _pyproject(
                authors=[{NAME_KEY: 'A'}, {NAME_KEY: 'B', 'email': 'b@e.g'}],
            ),
            METADATA_SECTION,
            'author',
            'A, B',
            id='authors',
        ),
        pytest.param(
            _dynamic_readme_pyproject(RST_README_CONFIG),
            METADATA_SECTION,
            'long_description',
            'file: README.rst, CHANGES.rst',
            id='dynamic-readme',
        ),
        pytest.param(
            _dynamic_readme_pyproject(RST_README_CONFIG),
            METADATA_SECTION,
            'long_description_content_type',
            'text/x-rst',
            id='readme-content-type',
        ),
        pytest.param(
            _pyproject({PACKAGES_KEY: ['pkg', 'pkg.sub']}),
            OPTIONS_SECTION,
            PACKAGES_KEY,
            '\npkg\npkg.sub',
            id='explicit-packages',
        ),
        pytest.param(
            _pyproject({PACKAGES_KEY: {'find': {'where': ['src']}}}),
            OPTIONS_SECTION,
            'package_dir',
            '\n= src',
            id='src-layout',
        ),
        pytest.param(
            _pyproject({'package-data': {'*': ['*.so']}}),
            'options.package_data',
            '*',
            '\n*.so',
            id='package-data',
        ),
    ),
)
def test_compat_setup_cfg_setting(
    pyproject: _t.Mapping[str, _t.Any],
    section: str,
    setting_name: str,
    expected_setting: str,
) -> None:
    """Check that a ``pyproject.toml`` setting gets into ``setup.cfg``."""
    rendered_config = _render_and_parse(pyproject)
    assert rendered_config[section][setting_name] == expected_setting


@pytest.mark.parametrize(
    ('pyproject', 'section', 'setting_name'),
    (
        pytest.param(
            _pyproject(license={'file': 'LICENSE'}),
            METADATA_SECTION,
            LICENSE_KEY,
            id='license-file-table',
        ),
        pytest.param(
            _pyproject(authors=[{NAME_KEY: 'A'}]),
            METADATA_SECTION,
            'author_email',
            id='authors-without-emails',
        ),
        pytest.param(
            _dynamic_readme_pyproject(
                UNTYPED_README_CONFIG,
                declared_dynamic=False,
            ),
            METADATA_SECTION,
            'long_description',
            id='readme-not-declared-dynamic',
        ),
        pytest.param(
            _dynamic_readme_pyproject(UNTYPED_README_CONFIG),
            METADATA_SECTION,
            'long_description_content_type',
            id='readme-without-content-type',
        ),
        pytest.param(
            _pyproject({PACKAGES_KEY: {'find': {}}}),
            OPTIONS_SECTION,
            'package_dir',
            id='flat-layout',
        ),
    ),
)
def test_compat_setup_cfg_omission(
    pyproject: _t.Mapping[str, _t.Any],
    section: str,
    setting_name: str,
) -> None:
    """Check that settings without a ``setup.cfg`` equivalent are left out."""
    rendered_config = _render_and_parse(pyproject)
    assert not rendered_config.has_option(section, setting_name)


def test_compat_setup_cfg_matches_pyproject(tmp_path: pathlib.Path) -> None:
    """Check that setuptools reads the same core metadata from both files."""
    setupcfg = pytest.importorskip('setuptools.config.setupcfg')
    pyprojecttoml = pytest.importorskip('setuptools.config.pyprojecttoml')
    pyproject_path = PROJECT_ROOT_DIR / PYPROJECT_TOML_NAME
    setup_cfg_path = tmp_path / SETUP_CFG_NAME
    setup_cfg_path.write_text(
        render_compat_setup_cfg(
            load_toml_from_string(
                pyproject_path.read_text(encoding=TEXT_ENCODING),
            ),
        ),
        encoding=TEXT_ENCODING,
    )
    for document_name in ('README.rst', 'CHANGELOG.rst', 'LICENSE.rst'):
        (tmp_path / document_name).write_bytes(
            (PROJECT_ROOT_DIR / document_name).read_bytes(),
        )

    # NOTE: Parsing from the temporary directory keeps installed setuptools
    # NOTE: plugins like setuptools-scm from acting on the checkout's own
    # NOTE: `pyproject.toml`:
    with chdir_cm(tmp_path):
        setup_cfg = setupcfg.read_configuration(str(setup_cfg_path))
        project = pyprojecttoml.read_configuration(str(pyproject_path))[
            'project'
        ]

    assert {
        pep621_key: setup_cfg[section][setup_cfg_key]
        for section, setup_cfg_key, pep621_key in EQUIVALENT_CORE_METADATA
    } == {
        pep621_key: project[pep621_key]
        for _section, _setup_cfg_key, pep621_key in EQUIVALENT_CORE_METADATA
    }
    assert setup_cfg[METADATA_SECTION][LICENSE_KEY] == _license_text(
        project[LICENSE_KEY],
    )
    assert (
        setup_cfg[METADATA_SECTION]['long_description']
        == project[README_KEY]['text']
    )
    # NOTE: `setup.cfg` parsing normalizes the specifier's whitespace:
    assert _normalize_specifier(
        setup_cfg[OPTIONS_SECTION]['python_requires'],
    ) == _normalize_specifier(project['requires-python'])


def test_compat_setup_cfg_written_temporarily(tmp_path: pathlib.Path) -> None:
    """Check that the compat ``setup.cfg`` only exists inside the context."""
    (tmp_path / PYPROJECT_TOML_NAME).write_text(
        MINIMAL_PYPROJECT_TOML,
        encoding=TEXT_ENCODING,
    )
    setup_cfg_path = tmp_path / SETUP_CFG_NAME

    with compat_setup_cfg_written(tmp_path):
        rendered_config = configparser.ConfigParser(interpolation=None)
        rendered_config.read_string(
            setup_cfg_path.read_text(encoding=TEXT_ENCODING),
        )
        assert rendered_config[METADATA_SECTION][NAME_KEY] == 'pkg'

    assert not setup_cfg_path.exists()


def test_compat_setup_cfg_keeps_existing_config(
    tmp_path: pathlib.Path,
) -> None:
    """Check that a pre-existing ``setup.cfg`` is left untouched."""
    (tmp_path / PYPROJECT_TOML_NAME).write_text(
        MINIMAL_PYPROJECT_TOML,
        encoding=TEXT_ENCODING,
    )
    setup_cfg_path = tmp_path / SETUP_CFG_NAME
    original_config = '[metadata]\nname = original\n'
    setup_cfg_path.write_text(original_config, encoding=TEXT_ENCODING)

    with compat_setup_cfg_written(tmp_path):
        assert (
            setup_cfg_path.read_text(encoding=TEXT_ENCODING) == original_config
        )

    assert setup_cfg_path.read_text(encoding=TEXT_ENCODING) == original_config
