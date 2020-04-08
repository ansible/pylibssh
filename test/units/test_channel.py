# -*- coding: utf-8 -*-

"""Tests suite for channel."""

from pylibsshext.channel import Channel


def test_make_channel():
    """Smoke-test Channel instance creation."""
    assert Channel()
