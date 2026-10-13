"""Sanity tests for sshd-related helpers."""

import pytest


MAX_PORT_NUMBER = 65535


@pytest.mark.usefixtures('ssh_client_session')
def test_sshd_addr_fixture_port(sshd_addr: tuple[str, int]) -> None:
    """Smoke-test sshd_addr fixture.

    # noqa: DAR101
    """
    _host, port = sshd_addr
    assert 0 < port <= MAX_PORT_NUMBER
