# -*- coding: utf-8 -*-

"""Tests suite for channel."""

import pytest


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
    'Ref: https://github.com/ansible/pylibssh/issues/57',  # noqa: WPS326
    run=False,
    strict=False,
)
@pytest.mark.forked
def test_exec_command(ssh_channel):
    """Test getting the output of a remotely executed command."""
    u_cmd_out = ssh_channel.exec_command('echo -n Hello World').stdout.decode()
    assert u_cmd_out == u'Hello World'  # noqa: WPS302


def test_double_close(ssh_channel):
    """Test that closing the channel multiple times doesn't explode."""
    for _ in range(3):  # noqa: WPS122
        ssh_channel.close()


def test_channel_exit_status(ssh_channel):
    """Test retrieving a channel exit status upon close."""
    ssh_channel.close()
    assert ssh_channel.get_channel_exit_status() == -1
