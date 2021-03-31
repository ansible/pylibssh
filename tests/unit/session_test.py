# -*- coding: utf-8 -*-

"""Tests suite for session."""

import pytest

from pylibsshext.errors import LibsshSessionException
from pylibsshext.session import Session


def test_make_session():
    """Smoke-test Session instance creation."""
    assert Session()


def test_session_connection_refused(free_port_num):
    """Test that connecting to a missing service raises an error."""
    error_msg = '^ssh connect failed: Connection refused$'
    ssh_session = Session()
    with pytest.raises(LibsshSessionException, match=error_msg):
        ssh_session.connect(host='127.0.0.1', port=free_port_num)
