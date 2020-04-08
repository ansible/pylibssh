# -*- coding: utf-8 -*-

"""Tests suite for sftp."""

from pylibsshext.sftp import SFTP


def test_make_sftp():
    """Smoke-test SFTP instance creation."""
    assert SFTP()
