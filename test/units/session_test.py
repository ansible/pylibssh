# -*- coding: utf-8 -*-

"""Tests suite for session."""

from pylibsshext.session import Session


def test_make_session():
    """Smoke-test Session instance creation."""
    assert Session()
