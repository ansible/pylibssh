# -*- coding: utf-8 -*-

"""Sanity tests for sshd-related helpers."""

MAX_PORT_NUMBER = 65535


def test_sshd_addr_fixture_port(sshd_addr, ssh_client_session):
    """Smoke-test sshd_addr fixture.

    # noqa: DAR101
    """
    _host, port = sshd_addr
    assert 0 < port <= MAX_PORT_NUMBER
