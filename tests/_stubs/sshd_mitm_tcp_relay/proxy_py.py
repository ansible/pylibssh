"""A proxy.py-based TCP relay in front of sshd."""

from __future__ import annotations

import contextlib
import pathlib
import typing as _t  # noqa: WPS111

import proxy
from proxy.common.flag import flags
from proxy.core.base import BaseTcpTunnelHandler
from proxy.core.connection import TcpServerConnection


if _t.TYPE_CHECKING:  # pragma: no cover
    from proxy.common.types import Readables, Writables

    from .types import HostPort


flags.add_argument(
    '--sshd-upstream-host',
    type=str,
    required=True,
    help='Hostname of the sshd to relay to.',
)
flags.add_argument(
    '--sshd-upstream-port',
    type=int,
    required=True,
    help='Port of the sshd to relay to.',
)
flags.add_argument(
    '--sshd-replies-paused-file',
    type=str,
    required=True,
    help='Sentinel file that, once it exists, pauses the sshd replies.',
)


class PausableSshdTunnelHandler(BaseTcpTunnelHandler):
    """Tunnel a TCP connection to sshd, optionally withholding its replies."""

    def initialize(self: _t.Self) -> None:
        """Connect to sshd right away since it speaks first."""
        super().initialize()
        self.upstream = TcpServerConnection(
            self.flags.sshd_upstream_host,
            self.flags.sshd_upstream_port,
        )
        self.upstream.connect()
        self._upstream_fileno = self.upstream.connection.fileno()

    def handle_data(self: _t.Self, client_bytes: memoryview) -> None:
        """Queue the client bytes for sshd.

        :param client_bytes: Bytes received from the client.
        """
        self.upstream.queue(client_bytes)

    async def handle_events(
        self: _t.Self,
        readables: Readables,
        writables: Writables,
    ) -> bool:
        """Handle the ready sockets, skipping sshd's ones while paused.

        :param readables: Sockets ready for reading.
        :param writables: Sockets ready for writing.
        :returns: Whether to tear the tunnel down.
        """
        # NOTE: The sentinel is checked before every pass that may read
        # NOTE: from sshd, so replies to anything sent after it got
        # NOTE: created are never forwarded. Omitting sshd's socket from
        # NOTE: `get_events()` would not work: proxy.py never unregisters
        # NOTE: sockets that drop out of it.
        #
        # NOTE: The blocking `stat()` is fine here: proxy.py's threadless
        # NOTE: loop around this coroutine blocks in `select()` anyway.
        if pathlib.Path(  # noqa: ASYNC240
            self.flags.sshd_replies_paused_file,
        ).exists():
            readables = [
                ready_sock
                for ready_sock in readables
                if ready_sock != self._upstream_fileno
            ]
        return await super().handle_events(readables, writables)


@contextlib.contextmanager
def run_sshd_relay(
    sshd_addr: HostPort,
    replies_paused_file: pathlib.Path,
) -> _t.Iterator[HostPort]:
    """Run proxy.py as a TCP relay in front of sshd.

    :param sshd_addr: Hostname and port tuple of the sshd to relay to.
    :param replies_paused_file: Sentinel file pausing the sshd replies.
    :yields: Hostname and port tuple of the relay.
    """
    hostname, port = sshd_addr
    proxypy_args = [
        f'--sshd-upstream-host={hostname!s}',
        f'--sshd-upstream-port={port:d}',
        f'--sshd-replies-paused-file={replies_paused_file!s}',
    ]
    # NOTE: The threadless mode runs the relay in separate processes,
    # NOTE: which is necessary because the Cython modules hold the GIL
    # NOTE: while blocking in libssh, which would starve relay threads.
    with proxy.Proxy(
        input_args=proxypy_args,
        work_klass=PausableSshdTunnelHandler,
        threadless=True,
        num_acceptors=1,
        num_workers=1,
        port=0,  # ephemeral port, so that kernel allocates a free one
    ) as proxy_instance:
        yield str(proxy_instance.flags.hostname), proxy_instance.flags.port
