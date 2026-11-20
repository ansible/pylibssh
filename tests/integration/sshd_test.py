"""Sanity tests for sshd-related helpers."""

import pathlib
import socket
import subprocess
import time
import typing as _t

import pytest

from pylibsshext.errors import LibsshSessionException
from pylibsshext.session import Session


MAX_PORT_NUMBER = 65535


@pytest.mark.usefixtures('ssh_client_session')
def test_sshd_addr_fixture_port(sshd_addr: tuple[str, int]) -> None:
    """Smoke-test sshd_addr fixture.

    # noqa: DAR101
    """
    _host, port = sshd_addr
    assert 0 < port <= MAX_PORT_NUMBER


def _port_accepts_connection(port: int) -> bool:
    """Check whether the given local port accepts a connection."""
    try:
        with socket.create_connection(('127.0.0.1', port), timeout=0.1):
            return True
    except OSError:
        return False


def _wait_until_listening(port: int, timeout: float = 10) -> None:
    """Wait until the given local port accepts a connection."""
    deadline = time.monotonic() + timeout
    while not _port_accepts_connection(port):
        if time.monotonic() > deadline:
            msg = 'sshd did not start listening'
            raise AssertionError(msg) from None
        time.sleep(0.1)


@pytest.fixture
def permissive_auth_sshd_addr(
    free_port_num: int,
    tmp_path: pathlib.Path,
) -> _t.Iterator[tuple[str, int]]:
    """Spawn an sshd that advertises the password, keyboard and GSSAPI methods."""
    hostkey_path = tmp_path / 'ssh_host_ecdsa_key'
    keygen_cmd = 'ssh-keygen', '-t', 'ecdsa', '-N', '', f'-f{hostkey_path!s}'
    subprocess.check_call(keygen_cmd)

    pid_file = tmp_path / 'sshd.pid'
    sshd_cmd = (
        '/usr/sbin/sshd',
        '-D',
        '-f/dev/null',
        '-E/dev/stderr',
        f'-oHostKey={hostkey_path!s}',
        f'-oPidFile={pid_file!s}',
        '-oUsePAM=yes',
        '-oPasswordAuthentication=yes',
        '-oKbdInteractiveAuthentication=yes',
        '-oGSSAPIAuthentication=yes',
        '-oPubkeyAuthentication=yes',
        '-oMaxAuthTries=20',
        '-oStrictModes=no',
        '-oPermitRootLogin=yes',
        f'-oPort={free_port_num!s}',
        '-oListenAddress=127.0.0.1',
    )
    sshd_proc = subprocess.Popen(sshd_cmd)
    _wait_until_listening(free_port_num)
    yield ('127.0.0.1', free_port_num)
    sshd_proc.terminate()
    sshd_proc.wait(timeout=10)


def test_connect_all_auth_methods_fail_raises(
    permissive_auth_sshd_addr: tuple[str, int],
    tmp_path: pathlib.Path,
) -> None:
    """Check that exhausting every authentication method raises."""
    untrusted_key_path = tmp_path / 'untrusted_ecdsa_key'
    keygen_cmd = 'ssh-keygen', '-tecdsa', '-N', '', f'-f{untrusted_key_path!s}'
    subprocess.check_call(keygen_cmd)

    session = Session()
    incorrect_password = 'incorrect-password'  # noqa: S105  # wrong on purpose
    with pytest.raises(LibsshSessionException):
        session.connect(
            host=permissive_auth_sshd_addr[0],
            port=permissive_auth_sshd_addr[1],
            user='root',
            password=incorrect_password,
            private_key=untrusted_key_path.read_bytes(),
            host_key_checking=False,
        )
