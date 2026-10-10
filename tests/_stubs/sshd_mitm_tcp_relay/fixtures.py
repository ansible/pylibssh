"""Fixtures for a TCP relay in front of sshd that can withhold its replies."""

import pathlib
import typing as _t  # noqa: WPS111
from functools import partial
from types import ModuleType

import pytest
from _service_utils import ensure_ssh_session_connected

from pylibsshext.session import Session

from .types import HostPort


@pytest.fixture
def sshd_replies_paused_file(tmp_path: pathlib.Path) -> pathlib.Path:
    """Locate a sentinel file that pauses the sshd replies in ``sshd_relay``.

    :param tmp_path: Temporary directory to hold the sentinel file.
    :returns: Path that stops forwarding the sshd replies once it exists.
    """
    return tmp_path / 'sshd-replies-paused'


@pytest.fixture(scope='session')
def sshd_mitm_tcp_relay_backend() -> ModuleType:
    """Import the relay backend, skipping when its dependencies are missing.

    :returns: The ``_stubs.sshd_mitm_tcp_relay.proxy_py`` module.
    """
    # NOTE: `proxy.py` is optional so that downstream packagers, who
    # NOTE: often lack it, can still run the rest of the test suite.
    relay_backend = pytest.importorskip('_stubs.sshd_mitm_tcp_relay.proxy_py')
    assert isinstance(relay_backend, ModuleType)
    return relay_backend


@pytest.fixture
def sshd_relay(
    sshd_mitm_tcp_relay_backend: ModuleType,
    sshd_addr: HostPort,
    sshd_replies_paused_file: pathlib.Path,
) -> _t.Iterator[HostPort]:
    """Spawn a TCP relay in front of sshd that can withhold its replies.

    :param sshd_mitm_tcp_relay_backend: The relay backend module.
    :param sshd_addr: Hostname and port tuple of the sshd to relay to.
    :param sshd_replies_paused_file: Sentinel file pausing the replies.
    :yields: Hostname and port tuple of the relay.
    """
    with sshd_mitm_tcp_relay_backend.run_sshd_relay(
        sshd_addr,
        sshd_replies_paused_file,
    ) as relay_addr:
        yield relay_addr


@pytest.fixture
def ssh_session_connect_via_relay(
    sshd_relay: HostPort,
    ssh_clientkey_path: pathlib.Path,
) -> _t.Callable[[Session], None]:
    """
    Authenticate existing session object against SSHD through a relay.

    It returns a function that takes session as parameter.

    :param sshd_relay: Hostname and port tuple of the relay.
    :param ssh_clientkey_path: Path to the client private key.
    :returns: Function that will connect the session.
    """
    return partial(
        ensure_ssh_session_connected,
        sshd_addr=sshd_relay,
        ssh_clientkey_path=ssh_clientkey_path,
    )
