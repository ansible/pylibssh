# -*- coding: utf-8 -*-

"""Tests for the version info representation."""

import pytest

from pylibsshext import (
    __full_version__, __libssh_version__, __version__, __version_info__,
)


pytestmark = pytest.mark.smoke


def test_dunder_version():
    """Check that the version string has at least 3 parts."""
    assert __version__.count('.') >= 2


def test_dunder_version_info():
    """Check that the version info tuple looks legitimate."""
    assert type(__version_info__) == tuple  # noqa: WPS516
    assert len(__version_info__) >= 3
    assert all(
        type(digit) == int  # noqa: WPS516
        for digit in __version_info__[:2]
    )


def test_dunder_full_version():
    """Check that the full version mentions the wrapper and the lib."""
    assert __version__ in __full_version__
    assert __libssh_version__ in __full_version__


def test_dunder_libssh_version():
    """Check that libssh version looks valid."""
    assert __libssh_version__.count('.') == 2
