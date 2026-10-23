"""Minimal ``setup.cfg`` for setuptools versions predating PEP 621.

setuptools learned to read the ``[project]`` table from
``pyproject.toml`` in v61. Downstreams stuck with older versions can
still build the sdist when it ships a ``setup.cfg`` with the same core
metadata, which this module renders from ``pyproject.toml``.
"""

from __future__ import annotations

import typing as _t
from configparser import ConfigParser
from contextlib import contextmanager
from io import StringIO
from operator import itemgetter

from ._compat import load_toml_from_string


if _t.TYPE_CHECKING:
    from collections import abc as _c
    from pathlib import Path


_SETUP_CFG_NAME = 'setup.cfg'
_PYPROJECT_TOML_NAME = 'pyproject.toml'

_OPTIONS_SECTION = 'options'
_PACKAGES_FIND_SECTION = 'options.packages.find'
_PEP621_NAME_KEY = 'name'
_PEP621_EMAIL_KEY = 'email'

_TomlTable = _t.Mapping[str, _t.Any]
_FieldRenderer = _t.Callable[[_t.Any], str]


def _as_multiline(lines: _c.Iterable[str]) -> str:
    return ''.join(f'\n{line!s}' for line in lines)


# PEP 621 key, `setup.cfg` key, and how to render the setting:
_METADATA_FIELDS: tuple[tuple[str, str, _FieldRenderer], ...] = (
    ('description', 'description', str),
    # NOTE: A PEP 639 license expression or the `text` of an older PEP 621
    # NOTE: license table maps onto `setup.cfg`, unlike a license `file`:
    (
        'license',
        'license',
        lambda license_: (
            license_ if isinstance(license_, str) else license_.get('text', '')
        ),
    ),
    ('license-files', 'license_files', _as_multiline),
    (
        'urls',
        'project_urls',
        lambda urls: _as_multiline(
            f'{label!s} = {url!s}' for label, url in urls.items()
        ),
    ),
    ('classifiers', 'classifiers', _as_multiline),
    ('keywords', 'keywords', _as_multiline),
)
_OPTIONS_FIELDS: tuple[tuple[str, str, _FieldRenderer], ...] = (
    ('requires-python', 'python_requires', str),
    ('dependencies', 'install_requires', _as_multiline),
)


def _render_fields(
    toml_table: _TomlTable,
    fields: _c.Iterable[tuple[str, str, _FieldRenderer]],
) -> dict[str, str]:
    rendered_fields = (
        (setup_cfg_key, render_field(toml_table[pep621_key]))
        for pep621_key, setup_cfg_key, render_field in fields
        if toml_table.get(pep621_key)
    )
    return dict(filter(itemgetter(1), rendered_fields))


def _render_people(
    people: _c.Iterable[_c.Mapping[str, str]],
) -> dict[str, str]:
    people = list(people)
    names = ', '.join(
        person[_PEP621_NAME_KEY]
        for person in people
        if _PEP621_NAME_KEY in person
    )
    emails = ', '.join(
        person[_PEP621_EMAIL_KEY]
        for person in people
        if _PEP621_EMAIL_KEY in person
    )
    return {
        setup_cfg_key: joined_people
        for setup_cfg_key, joined_people in (
            ('author', names),
            ('author_email', emails),
        )
        if joined_people
    }


def _render_readme(
    project: _TomlTable,
    dynamic_config: _TomlTable,
) -> dict[str, str]:
    readme_config = dynamic_config.get('readme', {})
    readme_files = readme_config.get('file')
    if 'readme' not in project.get('dynamic', ()) or not readme_files:
        return {}
    readme_file_list = ', '.join(readme_files)
    rendered_readme = {'long_description': f'file: {readme_file_list!s}'}
    content_type = readme_config.get('content-type')
    if content_type:
        rendered_readme['long_description_content_type'] = content_type
    return rendered_readme


def _render_packages(
    config: ConfigParser,
    setuptools_config: _TomlTable,
) -> None:
    packages = setuptools_config.get('packages', {})
    if isinstance(packages, list):
        config[_OPTIONS_SECTION]['packages'] = _as_multiline(packages)
        return

    find_config = packages.get('find')
    if find_config is None:
        return
    search_root = find_config.get('where', ['.'])[0]
    config[_OPTIONS_SECTION]['packages'] = 'find:'
    if search_root != '.':
        config[_OPTIONS_SECTION]['package_dir'] = f'\n= {search_root!s}'
    config[_PACKAGES_FIND_SECTION] = {'where': search_root}
    excluded = find_config.get('exclude')
    if excluded:
        config[_PACKAGES_FIND_SECTION]['exclude'] = _as_multiline(excluded)


def render_compat_setup_cfg(pyproject: _TomlTable) -> str:
    """Render the core metadata from ``pyproject.toml`` as ``setup.cfg``.

    :param pyproject: Parsed contents of ``pyproject.toml``.
    :returns: Text of an equivalent minimal ``setup.cfg``.
    """
    project = pyproject['project']
    setuptools_config = pyproject.get('tool', {}).get('setuptools', {})

    config = ConfigParser(interpolation=None)
    config['metadata'] = {
        _PEP621_NAME_KEY: project[_PEP621_NAME_KEY],
        **_render_fields(project, _METADATA_FIELDS),
        **_render_readme(project, setuptools_config.get('dynamic', {})),
        **_render_people(project.get('authors', ())),
    }
    config[_OPTIONS_SECTION] = {
        # NOTE: `pyproject.toml`-based configuration defaults to `true`,
        # NOTE: unlike `setup.cfg`:
        'include_package_data': str(
            setuptools_config.get('include-package-data', True),
        ),
        **_render_fields(project, _OPTIONS_FIELDS),
    }
    _render_packages(config, setuptools_config)
    package_data = setuptools_config.get('package-data')
    if package_data:
        config['options.package_data'] = dict(
            zip(package_data, map(_as_multiline, package_data.values())),
        )

    rendered_config = StringIO()
    config.write(rendered_config)
    return rendered_config.getvalue()


@contextmanager
def compat_setup_cfg_written(
    project_root: Path,
) -> _c.Generator[None, None, None]:
    """Provide a minimal ``setup.cfg`` for the duration of the context.

    Nothing is written when the project already has a ``setup.cfg``.

    :param project_root: Directory holding ``pyproject.toml``.
    :yields: None
    """
    setup_cfg_path = project_root / _SETUP_CFG_NAME
    if setup_cfg_path.exists():
        yield
        return

    pyproject = load_toml_from_string(
        (project_root / _PYPROJECT_TOML_NAME).read_text(encoding='utf-8'),
    )
    setup_cfg_path.write_text(
        render_compat_setup_cfg(pyproject),
        encoding='utf-8',
    )
    try:  # noqa: WPS501
        yield
    finally:
        setup_cfg_path.unlink()
