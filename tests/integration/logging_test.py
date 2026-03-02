"""Tests suite for logging."""

import contextlib as _ctx
import logging

import pytest

from pylibsshext.errors import LibsshSessionException
from pylibsshext.logging import ANSIBLE_PYLIBSSH_NOLOG, ANSIBLE_PYLIBSSH_TRACE
from pylibsshext.session import Session


LOCALHOST = '127.0.0.1'
BAD_LOG_LEVEL = 99


@pytest.fixture(autouse=True)
def _only_capture_project_logs(caplog: pytest.LogCaptureFixture) -> None:
    """Hide unrelated log entries from capture."""
    caplog.set_level(
        ANSIBLE_PYLIBSSH_NOLOG + 1,
    )  # suppress other loggers on the root level
    caplog.set_level(
        # NOTE: logging.NOTSET is unfit because it delegates to the root logger
        ANSIBLE_PYLIBSSH_TRACE - 1,  # capture beyond everything
        logger='ansible-pylibssh',
    )  # don't block things early
    caplog.clear()


def test_session_log_level_warning(
    caplog: pytest.LogCaptureFixture,
    free_port_num: int,
    libssh_version_tuple,
) -> None:
    """
    Test setting the log level to WARNING.

    It should show "Connection refused" on libssh 0.11.0 and newer.
    But no debug/ainfo/trace messages.
    """
    ssh_session = Session()
    ssh_session.set_log_level(logging.WARNING)

    # the connection will fail but first log lands before that
    with _ctx.suppress(LibsshSessionException):
        ssh_session.connect(host=LOCALHOST, port=free_port_num)

    log_records = caplog.records

    # This message is available only in libssh 0.11.0 and newer
    expected_substring = 'ssh_client_connection_callback: Connection refused'
    if libssh_version_tuple >= (0, 11, 0):
        assert any(
            record.levelname == 'WARNING' and expected_substring in record.msg
            for record in log_records
        )

    # No INFO and higher log messages should show up at this log level
    forbidden_levels = {logging.INFO, logging.DEBUG, ANSIBLE_PYLIBSSH_TRACE}
    captured_levels = {record.levelno for record in log_records}
    assert forbidden_levels.isdisjoint(captured_levels)


def test_session_log_level_debug(
    caplog: pytest.LogCaptureFixture,
    free_port_num: int,
) -> None:
    """
    Test setting the log level to DEBUG.

    It should reveal copyright information. But no trace messages.
    """
    ssh_session = Session()
    ssh_session.set_log_level(logging.DEBUG)

    # the connection will fail but first log lands before that
    with _ctx.suppress(LibsshSessionException):
        ssh_session.connect(host=LOCALHOST, port=free_port_num)

    log_records = caplog.records

    expected_copyright_substring = 'and libssh contributors.'
    # This log message is shown at different log levels
    # in different libssh versions. Changed at 657d9143d1 (before 0.11.0)
    # but backported to some RHEL9 versions so matching on the libssh version
    # is not reliable.
    assert any(
        record.levelname in {'DEBUG', 'INFO'}
        and expected_copyright_substring in record.msg
        for record in log_records
    )

    assert 'TRACE' not in (record.levelname for record in log_records)


def test_session_log_level_no_log(
    caplog: pytest.LogCaptureFixture,
    free_port_num: int,
) -> None:
    """Test setting the log level to NOLOG should be quiet."""
    ssh_session = Session()
    ssh_session.set_log_level(ANSIBLE_PYLIBSSH_NOLOG)

    # the connection will fail but first log lands before that
    with _ctx.suppress(LibsshSessionException):
        ssh_session.connect(host=LOCALHOST, port=free_port_num)

    assert not caplog.records


@pytest.mark.parametrize(
    'log_level',
    (ANSIBLE_PYLIBSSH_TRACE, logging.NOTSET),
    ids=('TRACE', 'NOTSET'),
)
def test_session_log_level_trace(
    caplog: pytest.LogCaptureFixture,
    free_port_num: int,
    log_level: int,
) -> None:
    """Test setting the most detailed log level provides all the logs."""
    ssh_session = Session()
    ssh_session.set_log_level(log_level)

    with _ctx.suppress(LibsshSessionException):
        ssh_session.connect(host=LOCALHOST, port=free_port_num)

    expected_poll_message = 'ssh_socket_pollcallback: Poll callback on socket'
    assert expected_poll_message in caplog.text


def test_session_log_level_bad():
    """Test that setting the log level to an unsupported value is rejected."""
    ssh_session = Session()

    error_msg = r'^Invalid log level \[99\]$'
    with pytest.raises(LibsshSessionException, match=error_msg):
        ssh_session.set_log_level(BAD_LOG_LEVEL)


def test_session_log_verbosity_session(
    caplog: pytest.LogCaptureFixture,
    free_port_num: int,
) -> None:
    """Test setting the log level through the Session initializer."""
    ssh_session = Session(log_verbosity=ANSIBLE_PYLIBSSH_TRACE)

    with _ctx.suppress(LibsshSessionException):
        ssh_session.connect(host=LOCALHOST, port=free_port_num)

    expected_poll_message = 'ssh_socket_pollcallback: Poll callback on socket'
    assert expected_poll_message in caplog.text
