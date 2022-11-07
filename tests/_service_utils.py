# -*- coding: utf-8 -*-

"""Test util helpers."""

import contextlib
import getpass
import socket
import sys
import time

from pylibsshext.errors import LibsshSessionException


IS_MACOS = sys.platform == 'darwin'
PY3_PLUS = sys.version_info[0] > 2
_MACOS_RECONNECT_ATTEMPT_DELAY = 0.06
_LINUX_RECONNECT_ATTEMPT_DELAY = 0.002
_DEFAULT_RECONNECT_ATTEMPT_DELAY = (
    _MACOS_RECONNECT_ATTEMPT_DELAY
    if IS_MACOS
    else _LINUX_RECONNECT_ATTEMPT_DELAY
)


@contextlib.contextmanager
def _socket():
    sock = socket.socket()
    try:  # noqa: WPS501
        yield sock
    finally:
        sock.close()


def _match_proto_start(sock, b_proto_id):
    while b_proto_id:
        buff = sock.recv(len(b_proto_id))
        if not buff or not b_proto_id.startswith(buff):
            raise RuntimeError(
                'The remote service did not send '
                'expected identifier string',  # noqa: WPS326
            )
        b_proto_id = b_proto_id[len(buff):]


def wait_for_svc_ready_state(  # noqa: WPS317
        host, port, protocol_identifier,  # noqa: WPS318
        max_conn_attempts=40,
        reconnect_attempt_delay=_DEFAULT_RECONNECT_ATTEMPT_DELAY,
):
    """Verify that the serivce is up and running.

    :param host: Hostname.
    :type host: str

    :param port: Port.
    :type port: int

    :param protocol_identifier: Protocol start string.
    :type protocol_identifier: bytes

    :param max_conn_attempts: Number of tries when connecting.
    :type max_conn_attempts: int

    :param reconnect_attempt_delay: Time to sleep between retries.
    :type reconnect_attempt_delay: float

    # noqa: DAR401
    """
    connection_errors = (ConnectionError if PY3_PLUS else socket.error,)

    for attempt_num in range(1, max_conn_attempts + 1):
        with _socket() as sock:
            if attempt_num >= max_conn_attempts:
                connection_errors = ()

            try:
                sock.connect((host, port))
            except connection_errors:
                time.sleep(reconnect_attempt_delay)
            else:
                _match_proto_start(sock, protocol_identifier)
                break


def _is_retriable_connection_error(ssh_sess_exc):
    connection_error_msg = str(ssh_sess_exc)
    retriable_connection_error_messages = (
        'Connection refused',
        'Connection reset by peer',
    )
    return any(
        msg in connection_error_msg
        for msg in retriable_connection_error_messages
    )


def ensure_ssh_session_connected(  # noqa: WPS317
        ssh_session, sshd_addr, ssh_clientkey_path,  # noqa: WPS318
        max_conn_attempts=40,
        reconnect_attempt_delay=_DEFAULT_RECONNECT_ATTEMPT_DELAY,
):
    """Attempt connecting to the SSH server until successful.

    :param ssh_session: SSH session object.
    :type ssh_session: pylibsshext.session.Session

    :param sshd_addr: Hostname and port tuple.
    :type sshd_addr: tuple[str, int]

    :param ssh_clientkey_path: Hostname and port tuple.
    :type ssh_clientkey_path: pathlib.Path

    :param max_conn_attempts: Number of tries when connecting.
    :type max_conn_attempts: int

    :param reconnect_attempt_delay: Time to sleep between retries.
    :type reconnect_attempt_delay: float
    """
    hostname, port = sshd_addr
    for attempt_num in range(1, max_conn_attempts + 1):
        try:  # noqa: WPS503
            ssh_session.connect(
                host=hostname,
                port=port,
                user=getpass.getuser(),
                private_key=ssh_clientkey_path.read_bytes(),
                host_key_checking=False,
                look_for_keys=False,
            )
        except LibsshSessionException as ssh_sess_exc:
            if not _is_retriable_connection_error(ssh_sess_exc):
                raise

            time.sleep(reconnect_attempt_delay)
        else:
            return

    raise TimeoutError('Timed out waiting for a successful connection')
