# -*- coding: utf-8 -*-

"""Tests suite for channel."""

import sys

import pytest

# isort: on  # noqa: E800

try:  # noqa: WPS229  # session imports channel under the hood too
    from pylibsshext.channel import Channel  # noqa: WPS433
    from pylibsshext.session import Session
except ImportError:
    if sys.version_info[0] != 2:
        raise
    pytestmark = pytest.mark.skip(
        sys.version_info[0] == 2,
        reason='Channel import fails under Python 2',
    )
else:
    pytestmark = pytest.mark.xfail(
        sys.version_info[0] == 2,
        reason='Channel import fails under Python 2',
    )


@pytest.mark.xfail(
    reason='Fails for an unknown reason',
    raises=MemoryError,
)
def test_make_channel():
    """Smoke-test Channel instance creation."""
    assert Channel(Session())
