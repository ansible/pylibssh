"""Test util helpers."""

import getpass
import multiprocessing
import selectors
import socket
import subprocess
import sys
import time
from multiprocessing.synchronize import Event as ProcessEvent


IS_MACOS = sys.platform == 'darwin'
_MACOS_RECONNECT_ATTEMPT_DELAY = 0.06
_LINUX_RECONNECT_ATTEMPT_DELAY = 0.002
_DEFAULT_RECONNECT_ATTEMPT_DELAY = (
    _MACOS_RECONNECT_ATTEMPT_DELAY
    if IS_MACOS
    else _LINUX_RECONNECT_ATTEMPT_DELAY
)
_RELAY_CHUNK_SIZE = 65536
_RELAY_SHUTDOWN_TIMEOUT_SEC = 5

HostPort = tuple[str, int]


def wait_for_svc_ready_state(
    host,
    port,
    clientkey_path,
    max_conn_attempts=40,
    reconnect_attempt_delay=_DEFAULT_RECONNECT_ATTEMPT_DELAY,
):
    """Verify that the service is up and running.

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

    attempts = 0
    rc = -1
    while attempts < max_conn_attempts and rc != 0:
        check_result = subprocess.run(cmd, check=False)
        rc = check_result.returncode
        if rc != 0:
            time.sleep(reconnect_attempt_delay)

    if rc != 0:
        timeout_msg = 'Timed out waiting for a successful connection'
        raise TimeoutError(timeout_msg)


def ensure_ssh_session_connected(
    ssh_session,
    sshd_addr,
    ssh_clientkey_path,
    ssh_session_retries=0,
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
        open_session_retries=ssh_session_retries,
    )


def _forward_chunk(source: socket.socket, destination: socket.socket) -> bool:
    chunk = source.recv(_RELAY_CHUNK_SIZE)
    destination.sendall(chunk)
    return bool(chunk)


def _relay_ready_sockets(
    selector: selectors.BaseSelector,
    peers: dict[socket.socket, socket.socket],
    upstream: socket.socket,
    replies_paused: ProcessEvent,
) -> bool:
    for selector_key, _events in selector.select():
        source = selector_key.fileobj
        # NOTE: The event is checked before every upstream read, so
        # NOTE: replies to anything sent after it got set are never
        # NOTE: forwarded.
        if source is upstream and replies_paused.is_set():
            selector.unregister(upstream)
        elif not _forward_chunk(source, peers[source]):
            return False
    return True


def relay_tcp_traffic(
    listener: socket.socket,
    upstream_addr: HostPort,
    replies_paused: ProcessEvent,
) -> None:
    """Forward a single TCP connection to an upstream address.

    Once ``replies_paused`` is set, the upstream bytes are left unread
    while the downstream ones keep being forwarded.

    :param listener: Listening socket to accept the downstream from.
    :param upstream_addr: Hostname and port tuple to forward to.
    :param replies_paused: Event that stops forwarding upstream bytes.
    """
    downstream, _downstream_addr = listener.accept()
    upstream = socket.create_connection(upstream_addr)
    peers = {downstream: upstream, upstream: downstream}
    with selectors.DefaultSelector() as selector:
        for peer_sock in peers:
            selector.register(peer_sock, selectors.EVENT_READ)
        is_relaying = True
        while is_relaying:
            is_relaying = _relay_ready_sockets(
                selector,
                peers,
                upstream,
                replies_paused,
            )


def stop_relay(relay: multiprocessing.Process) -> None:
    """Wait for the relay process to exit, terminating it if it hangs.

    :param relay: Process running :func:`relay_tcp_traffic`.
    """
    # NOTE: The relay exits once the client disconnects. It is only
    # NOTE: terminated if that does not happen in time, such as when
    # NOTE: the client never connected.
    relay.join(timeout=_RELAY_SHUTDOWN_TIMEOUT_SEC)
    relay.terminate()
    relay.join()
