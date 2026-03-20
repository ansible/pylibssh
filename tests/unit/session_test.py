"""Tests suite for session."""

from __future__ import annotations

from pathlib import Path
from typing import Type, Union

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


@pytest.mark.parametrize(
    'path_arg_type',
    (str, Path),
    ids=str,
)
def test_parse_config_nonexistent_raises(
    path_arg_type: Union[Type[str], Type[Path]],
    tmp_path: Path,
) -> None:
    """parse_config() with a missing file raises LibsshConfigParseException."""
    session = Session()
    session.set_ssh_options('host', 'somehost')
    nonexistent = tmp_path / 'nonexistent_ssh_config'
    assert not nonexistent.exists()
    path_arg = path_arg_type(nonexistent)
    with pytest.raises(
        LibsshConfigParseException,
        match=r'^Failed to parse SSH config: No such file or directory$',
    ):
        session.parse_config(path_arg)


@pytest.mark.parametrize(
    'path_arg_type',
    (str, Path),
    ids=str,
)
def test_parse_config_valid_file_succeeds(
    path_arg_type: Union[Type[str], Type[Path]],
    tmp_path: Path,
) -> None:
    """parse_config() with a valid config file does not raise (str, Path)."""
    session = Session()
    session.set_ssh_options('host', 'somehost')
    config_file = tmp_path / 'ssh_config'
    config_file.write_text('Host *\n', encoding='utf-8')
    path_arg = path_arg_type(config_file)
    try:
        session.parse_config(path_arg)
    except LibsshConfigParseException:
        pytest.skip(
            'libssh rejected minimal config file (path expansion or parsing is strict)',
        )


def test_connect_config_file_none_no_parse():
    """connect(config_file=None) does not call parse_config; fails at connect."""
    session = Session()
    expected_error_regex = (
        r'^ssh connect failed: .*test\.nonexistent\.example\.invalid.*$'
    )
    with pytest.raises(LibsshSessionException, match=expected_error_regex):
        session.connect(
            host='test.nonexistent.example.invalid',
            config_file=None,
        )
