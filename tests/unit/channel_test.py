# -*- coding: utf-8 -*-

"""Tests suite for channel."""

import pytest

from pylibsshext.channel import Channel
from pylibsshext.session import Session


@pytest.mark.xfail(
    reason='Fails for an unknown reason',
    raises=MemoryError,
)
def test_make_channel():
    """Smoke-test Channel instance creation."""
    assert Channel(Session())
