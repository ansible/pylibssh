"""Tests for the in-tree PEP 517 build backend."""

import configparser
import os
import pathlib
import shlex
import sys
import sysconfig
import typing as _t  # noqa: WPS111
from types import MappingProxyType

import pytest

from pep517_backend._compat import chdir_cm, load_toml_from_string
from pep517_backend._compat_setup_cfg import (
    compat_setup_cfg_written,
    render_compat_setup_cfg,
)
from pep517_backend._cython_configuration import patched_env


CFLAGS_VAR = 'CFLAGS'
CPPFLAGS_VAR = 'CPPFLAGS'
TRACE_MACRO = '-DCYTHON_TRACE_NOGIL=1'
SYS_MONITORING_MACRO = '-DCYTHON_USE_SYS_MONITORING=0'

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
NO_SETUPTOOLS_CONFIG: _t.Mapping[str, _t.Any] = MappingProxyType({})
NAME_KEY = 'name'
RST_README_CONFIG: _t.Mapping[str, _t.Any] = MappingProxyType(
    {
        'file': ['README.rst', 'CHANGES.rst'],
        'content-type': 'text/x-rst',
    },
)
UNTYPED_README_CONFIG: _t.Mapping[str, _t.Any] = MappingProxyType(
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
    monkeypatch: pytest.MonkeyPatch,
    *,
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
    sys.platform == 'win32',
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
