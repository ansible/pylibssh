"""Tests suite for session."""

import pytest

from pylibsshext.errors import LibsshSessionException
from pylibsshext.session import Session


def test_make_session() -> None:
    """Smoke-test Session instance creation."""
    assert Session()


def test_make_session_close_connect() -> None:
    """Make sure the session is usable after call to close()."""
    session = Session()
    session.close()
    error_msg = '^ssh connect failed: Hostname required$'
    with pytest.raises(LibsshSessionException, match=error_msg):
        session.connect()


def test_session_connection_refused(free_port_num: int) -> None:
    """Test that connecting to a missing service raises an error."""
    error_msg = '^ssh connect failed: Connection refused$'
    ssh_session = Session()
    with pytest.raises(LibsshSessionException, match=error_msg):
        ssh_session.connect(host='127.0.0.1', port=free_port_num)
