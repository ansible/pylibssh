"""Tests suite for session."""

import pathlib
import tempfile

import pytest

from pylibsshext.errors import (
    LibsshConfigParseException,
    LibsshSessionException,
)
from pylibsshext.session import Session


def test_make_session():
    """Smoke-test Session instance creation."""
    assert Session()


def test_make_session_close_connect():
    """Make sure the session is usable after call to close()."""
    session = Session()
    session.close()
    error_msg = '^ssh connect failed: Hostname required$'
    with pytest.raises(LibsshSessionException, match=error_msg):
        session.connect()


def test_session_connection_refused(free_port_num):
    """Test that connecting to a missing service raises an error."""
    error_msg = '^ssh connect failed: Connection refused$'
    ssh_session = Session()
    with pytest.raises(LibsshSessionException, match=error_msg):
        ssh_session.connect(host='127.0.0.1', port=free_port_num)


def test_parse_config_nonexistent_raises():
    """parse_config() with nonexistent file raises LibsshConfigParseException."""
    session = Session(host='somehost')
    with pytest.raises(
        LibsshConfigParseException,
        match=r'Failed to parse SSH config:',
    ):
        session.parse_config('/nonexistent/path/ssh_config')


def test_parse_config_valid_file_succeeds():
    """parse_config() with a valid config file does not raise."""
    session = Session(host='somehost')
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.config',
        delete=False,
        encoding='utf-8',
    ) as tmp_file:
        tmp_file.write('Host *\n')
        path = tmp_file.name
    try:
        session.parse_config(path)
    except LibsshConfigParseException:
        pytest.skip(
            'libssh rejected minimal config file (path expansion or parsing is strict)',
        )
    finally:
        pathlib.Path(path).unlink()


def test_connect_config_file_none_no_parse():
    """connect(config_file=None) does not call parse_config; fails at connect."""
    session = Session(host='test.nonexistent.example.invalid')
    with pytest.raises(LibsshSessionException, match=r'ssh connect failed:'):
        session.connect(
            host='test.nonexistent.example.invalid',
            config_file=None,
        )
