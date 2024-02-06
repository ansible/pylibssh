# -*- coding: utf-8 -*-

"""Test util helpers."""

import getpass
import subprocess
import sys
import time


IS_MACOS = sys.platform == 'darwin'
_MACOS_RECONNECT_ATTEMPT_DELAY = 0.06
_LINUX_RECONNECT_ATTEMPT_DELAY = 0.002
_DEFAULT_RECONNECT_ATTEMPT_DELAY = (
    _MACOS_RECONNECT_ATTEMPT_DELAY
    if IS_MACOS
    else _LINUX_RECONNECT_ATTEMPT_DELAY
)


def wait_for_svc_ready_state(
    host,
    port,
    clientkey_path,
    max_conn_attempts=40,
    reconnect_attempt_delay=_DEFAULT_RECONNECT_ATTEMPT_DELAY,
):
    """Verify that the serivce is up and running.

    :param host: Hostname.
    :type host: str

    :param port: Port.
    :type port: int

    :param clientkey_path: Path to the client private key.
    :type clientkey_path: pathlib.Path

    :param max_conn_attempts: Number of tries when connecting.
    :type max_conn_attempts: int

    :param reconnect_attempt_delay: Time to sleep between retries.
    :type reconnect_attempt_delay: float

    # noqa: DAR401
    """
    cmd = [  # noqa: WPS317
        '/usr/bin/ssh',
        '-l', getpass.getuser(),
        '-i', str(clientkey_path),
        '-p', str(port),
        '-o', 'UserKnownHostsFile=/dev/null',
        '-o', 'StrictHostKeyChecking=no',
        host,
        '--', 'exit 0',
    ]

    attempts = 0
    rc = -1
    while attempts < max_conn_attempts and rc != 0:
        check_result = subprocess.run(cmd)
        rc = check_result.returncode
        if rc != 0:
            time.sleep(reconnect_attempt_delay)

    if rc != 0:
        raise TimeoutError('Timed out waiting for a successful connection')


def ensure_ssh_session_connected(  # noqa: WPS317
        ssh_session, sshd_addr, ssh_clientkey_path,  # noqa: WPS318
):
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
    )
