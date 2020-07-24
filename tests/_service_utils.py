# -*- coding: utf-8 -*-

"""Test util helpers."""

import contextlib
import socket
import sys
import time


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
        max_conn_attempts=20,
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
    connection_errors = (ConnectionError if PY3_PLUS else socket.error, )

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
