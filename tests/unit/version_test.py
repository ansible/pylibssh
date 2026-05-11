"""Tests for the version info representation."""

import pytest

from pylibsshext import (
    __full_version__,
    __libssh_version__,
    __version__,
    __version_info__,
)
from pylibsshext._version import (
    __full_version__ as _fv,
    __libssh_version__ as _lv,
    __version__ as _v,
    __version_info__ as _vi,
)


pytestmark = pytest.mark.smoke


def test_dunder_version():
    """Check that the version string has at least 3 parts."""
    assert __version__.count('.') >= 2


def test_dunder_version_info():
    """Check that the version info tuple looks legitimate."""
    assert isinstance(__version_info__, tuple)
    assert len(__version_info__) >= 3
    assert all(isinstance(digit, int) for digit in __version_info__[:2])


def test_dunder_full_version():
    """Check that the full version mentions the wrapper and the lib."""
    assert __version__ in __full_version__
    assert __libssh_version__ in __full_version__


def test_dunder_libssh_version():
    """Check that libssh version looks valid."""
    assert __libssh_version__.count('.') == 2


class TestVersionModule:
    """Tests for _version.py module internals."""

    def test_version_module_exports_match_package(self):
        """Test that _version module exports match package-level exports."""
        assert _v == __version__
        assert _vi == __version_info__
        assert _fv == __full_version__
        assert _lv == __libssh_version__

    def test_full_version_format(self):
        """Test __full_version__ has expected format with angle brackets."""
        assert __full_version__.startswith('<pylibsshext v')
        assert __full_version__.endswith('>')
        assert 'libssh v' in __full_version__

    def test_version_info_is_tuple(self):
        """Test __version_info__ is a tuple of parsed version components."""
        assert isinstance(__version_info__, tuple)
        assert __version_info__[0] == int(__version__.split('.')[0])
        assert __version_info__[1] == int(__version__.split('.')[1])

    def test_version_is_string(self):
        """Test __version__ is a string."""
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_libssh_version_is_string(self):
        """Test __libssh_version__ is a string."""
        assert isinstance(__libssh_version__, str)
        assert len(__libssh_version__) > 0

    def test_libssh_version_components_are_numeric(self):
        """Test that libssh version parts are numeric."""
        parts = __libssh_version__.split('.')
        assert len(parts) == 3
        for part in parts:
            assert part.isdigit(), f'Non-numeric version part: {part}'


class TestScmVersion:
    """Tests for _scm_version.py module."""

    def test_scm_version_exports(self):
        """Test _scm_version module exports expected names."""
        from pylibsshext._scm_version import (  # noqa: F401
            __commit_id__,
            __version__,
            __version_tuple__,
            commit_id,
            version,
            version_tuple,
        )

    def test_scm_version_consistency(self):
        """Test _scm_version aliases are consistent."""
        from pylibsshext._scm_version import (
            __commit_id__,
            __version__,
            __version_tuple__,
            commit_id,
            version,
            version_tuple,
        )
        assert version == __version__
        assert version_tuple == __version_tuple__
        assert commit_id == __commit_id__

    def test_scm_version_tuple_is_tuple(self):
        """Test _scm_version version_tuple is a tuple."""
        from pylibsshext._scm_version import version_tuple
        assert isinstance(version_tuple, tuple)
        assert len(version_tuple) >= 2

    def test_scm_version_all_list(self):
        """Test _scm_version __all__ contains expected names."""
        from pylibsshext._scm_version import __all__
        expected = [
            '__version__', '__version_tuple__', 'version',
            'version_tuple', '__commit_id__', 'commit_id',
        ]
        for name in expected:
            assert name in __all__, f'{name} not in __all__'
