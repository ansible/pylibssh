"""Test util helpers."""

from __future__ import annotations

import getpass
import subprocess
import sys
import time
import typing as _t  # noqa: WPS111


if _t.TYPE_CHECKING:
    import pathlib

    from pylibsshext.session import Session


IS_MACOS = sys.platform == 'darwin'
_MACOS_RECONNECT_ATTEMPT_DELAY = 0.06
_LINUX_RECONNECT_ATTEMPT_DELAY = 0.002
_DEFAULT_RECONNECT_ATTEMPT_DELAY = (
    _MACOS_RECONNECT_ATTEMPT_DELAY
    if IS_MACOS
    else _LINUX_RECONNECT_ATTEMPT_DELAY
)


def wait_for_svc_ready_state(
    host: str,
    port: int,
    clientkey_path: pathlib.Path,
    timeout_seconds: float = 10,
    reconnect_attempt_delay: float = _DEFAULT_RECONNECT_ATTEMPT_DELAY,
) -> None:
    """Verify that the service is up and running.

    :param host: Hostname.
    :type host: str

    :param port: Port.
    :type port: int

    :param clientkey_path: Path to the client private key.
    :type clientkey_path: pathlib.Path

    :param timeout_seconds: For how long to keep retrying to connect.
    :type timeout_seconds: float

    :param reconnect_attempt_delay: Time to sleep between retries.
    :type reconnect_attempt_delay: float

    # noqa: DAR401
    """
    cmd = [
        '/usr/bin/ssh',
        '-F/dev/null',  # or -Fnone
        '-oConnectTimeout=1',
        '-oIdentitiesOnly=yes',
        '-oIdentityAgent=/dev/null',
        f'-oIdentityFile={clientkey_path!s}',
        '-oPasswordAuthentication=no',
        f'-oPort={port!s}',
        '-oPreferredAuthentications=publickey',
        '-oStrictHostKeyChecking=no',
        f'-oUser={getpass.getuser()!s}',
        '-oUserKnownHostsFile=/dev/null',
        host,
        '--',
        'exit 0',
    ]

    deadline = time.monotonic() + timeout_seconds
    rc = -1
    while rc != 0 and time.monotonic() < deadline:
        check_result = subprocess.run(cmd, check=False)
        rc = check_result.returncode
        if rc != 0:
            time.sleep(reconnect_attempt_delay)

    if rc != 0:
        timeout_msg = 'Timed out waiting for a successful connection'
        raise TimeoutError(timeout_msg)


def ensure_ssh_session_connected(
    ssh_session: Session,
    sshd_addr: tuple[str, int],
    ssh_clientkey_path: pathlib.Path,
    ssh_session_retries: int = 0,
) -> None:
    """Attempt connecting to the SSH server until successful.

    :param ssh_session: SSH session object.
    :type ssh_session: pylibsshext.session.Session

    :param sshd_addr: Hostname and port tuple.
    :type sshd_addr: tuple[str, int]

    :param ssh_clientkey_path: Hostname and port tuple.
    :type ssh_clientkey_path: pathlib.Path
    """
    hostname, port = sshd_addr
    ssh_session.connect(
        host=hostname,
        port=port,
        user=getpass.getuser(),
        private_key=ssh_clientkey_path.read_bytes(),
        host_key_checking=False,
        look_for_keys=False,
        open_session_retries=ssh_session_retries,
    )
