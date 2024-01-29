# -*- coding: utf-8 -*-

"""Tests suite for channel."""

import signal
import time

import pytest


COMMAND_TIMEOUT = 30
POLL_EXIT_CODE_TIMEOUT = 5
POLL_TIMEOUT = 5000


@pytest.fixture
def ssh_channel(ssh_client_session):
    """Initialize a channel and tear it down after testing.

    :param ssh_client_session: A pre-authenticated SSH session.
    :type ssh_client_session: pylibsshext.session.Session

    :yields: A libssh channel instance.
    :ytype: pylibsshext.channel.Channel
    """
    chan = ssh_client_session.new_channel()
    try:  # noqa: WPS501
        yield chan
    finally:
        chan.close()


@pytest.mark.xfail(
    reason='This test causes SEGFAULT, flakily. '
    'Ref: https://github.com/ansible/pylibssh/issues/57',
    strict=False,
)
@pytest.mark.forked
def test_exec_command(ssh_channel):
    """Test getting the output of a remotely executed command."""
    u_cmd_out = ssh_channel.exec_command('echo -n Hello World').stdout.decode()
    assert u_cmd_out == u'Hello World'  # noqa: WPS302
    # Test that repeated calls to exec_command do not segfault.
    u_cmd_out = ssh_channel.exec_command('echo -n Hello Again').stdout.decode()
    assert u_cmd_out == u'Hello Again'  # noqa: WPS302


def test_double_close(ssh_channel):
    """Test that closing the channel multiple times doesn't explode."""
    for _ in range(3):  # noqa: WPS122
        ssh_channel.close()


def test_channel_exit_status(ssh_channel):
    """Test retrieving a channel exit status upon close."""
    ssh_channel.close()
    assert ssh_channel.get_channel_exit_status() == -1


def test_read_bulk_response(ssh_client_session):
    """Test getting the output of a remotely executed command."""
    ssh_shell = ssh_client_session.invoke_shell()
    ssh_shell.sendall(b'echo -n Hello World')
    response = b''
    timeout = 2
    while b'Hello World' not in response:
        response += ssh_shell.read_bulk_response()
        time.sleep(timeout)
        timeout += 2
        if timeout == COMMAND_TIMEOUT:
            break

    assert b'Hello World' in response  # noqa: WPS302


def test_request_exec(ssh_channel):
    """Test direct call to request_exec."""
    ssh_channel.request_exec('exit 1')

    rc = -1
    while rc == -1:
        ssh_channel.poll(timeout=POLL_EXIT_CODE_TIMEOUT)
        rc = ssh_channel.get_channel_exit_status()
    assert rc == 1


def test_send_eof(ssh_channel):
    """Test send_eof correctly terminates input stream."""
    ssh_channel.request_exec('cat')
    ssh_channel.send_eof()

    rc = -1
    while rc == -1:
        ssh_channel.poll(timeout=POLL_EXIT_CODE_TIMEOUT)
        rc = ssh_channel.get_channel_exit_status()
    assert rc == 0


def test_send_signal(ssh_channel):
    """Test send_signal correctly forwards signal to the process."""
    ssh_channel.request_exec('bash -c \'trap "exit 1" SIGUSR1; echo ready; sleep 5; exit 0\'')

    # Wait until the process is ready to receive signal
    output = ''
    while not output.startswith('ready'):
        ssh_channel.poll(timeout=POLL_TIMEOUT)
        output += ssh_channel.recv().decode('utf-8')

    # Send SIGINT
    ssh_channel.send_signal(signal.SIGUSR1)

    rc = -1
    while rc == -1:
        ssh_channel.poll(timeout=POLL_EXIT_CODE_TIMEOUT)
        rc = ssh_channel.get_channel_exit_status()

    assert rc == 1


def test_recv_eof(ssh_channel):
    """
    Test that reading EOF does not raise error.

    SystemError: Negative size passed to PyBytes_FromStringAndSize
    """
    ssh_channel.request_exec('exit 0')
    ssh_channel.poll(timeout=POLL_TIMEOUT)
    assert ssh_channel.is_eof
    ssh_channel.recv()
