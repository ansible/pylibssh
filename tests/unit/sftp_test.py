# -*- coding: utf-8 -*-

"""Tests suite for sftp."""

import pytest
# isort: on  # noqa: E800
from pylibsshext.errors import LibsshSFTPException
from pylibsshext.session import Session
from pylibsshext.sftp import SFTP


@pytest.mark.xfail(
    reason='Fails for an unknown reason',
    raises=LibsshSFTPException,
)
def test_make_sftp():
    """Smoke-test SFTP instance creation."""
    assert SFTP(Session())
