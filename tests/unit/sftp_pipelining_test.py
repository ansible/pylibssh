"""Tests suite for SFTP transfer pipelining."""

from __future__ import annotations

import contextlib
import pathlib
import random
import typing as _t


if _t.TYPE_CHECKING:
    from collections import abc as _c

    from pylibsshext.session import Session


import pytest

from pylibsshext.sftp import (
    SFTP,
    SFTP_MAX_CHUNK,
    SFTP_MAX_CHUNK_LIMIT,
    _RemoteFile,
)

from pylibsshext import __libssh_version__


PIPELINED_CHUNKS_COUNT = 15

LIBSSH_VERSION = tuple(map(int, __libssh_version__.split('.')))
requires_aio_support = pytest.mark.skipif(
    LIBSSH_VERSION < (0, 11, 0),
    reason='Asynchronous SFTP requires libssh >= 0.11.0',
)


class _RemoteFileCounterProxy:
    """Proxy context manager to count I/O calls on remote file."""

    instances: _t.ClassVar[list[_RemoteFileCounterProxy]] = []
    real_cm: _t.ClassVar[_c.Callable[..., _RemoteFile] | None] = None

    def __init__(
        self: _RemoteFileCounterProxy,
        target: _RemoteFile,
    ) -> None:
        self.io_calls = 0
        self._target = target

    def write(self: _RemoteFileCounterProxy, chunk: memoryview) -> int:
        self.io_calls += 1
        return int(self._target.write(chunk))

    def readinto(self: _RemoteFileCounterProxy, buf: bytearray) -> int:
        self.io_calls += 1
        return int(self._target.readinto(buf))


@contextlib.contextmanager
def _tracking_remote_file_cm(
    *,
    flags: int,
    path: str,
    sftp_obj: SFTP,
) -> _t.Generator[_RemoteFileCounterProxy, None, None]:
    """Yield counting proxy wrapping the real remote file context manager."""
    assert _RemoteFileCounterProxy.real_cm is not None
    with _RemoteFileCounterProxy.real_cm(
        flags=flags,
        path=path,
        sftp_obj=sftp_obj,
    ) as target:
        proxy = _RemoteFileCounterProxy(target)
        _RemoteFileCounterProxy.instances.append(proxy)
        yield proxy


@pytest.fixture
def sftp_session(ssh_client_session: Session) -> _t.Iterator[SFTP]:
    """Initialize an SFTP session and destroy it after testing."""
    sftp_sess = ssh_client_session.sftp()
    yield sftp_sess
    sftp_sess.close()


@pytest.fixture
def transmit_payload(request: pytest.FixtureRequest) -> bytes:
    """Generate binary test payloads of assorted sizes."""
    payload_len = request.param
    assert isinstance(payload_len, int)
    return random.randbytes(payload_len)


@pytest.fixture
def dst_path(tmp_path: pathlib.Path) -> pathlib.Path:
    """Return a data destination path."""
    path = tmp_path / 'dst-file.txt'
    assert not path.exists()
    return path


@pytest.fixture
def src_path(
    tmp_path: pathlib.Path,
    transmit_payload: bytes,
) -> pathlib.Path:
    """Return a populated data source path."""
    path = tmp_path / 'src-file.txt'
    path.write_bytes(transmit_payload)
    return path


@pytest.fixture
def _small_sftp_limits(
    monkeypatch: pytest.MonkeyPatch,
    sftp_session: SFTP,
    transmit_payload: bytes,
) -> None:
    """Monkeypatch SFTP chunk size limits based on payload length to exercise pipelining."""
    chunk_size = max(1, len(transmit_payload) // PIPELINED_CHUNKS_COUNT)
    monkeypatch.setattr('pylibsshext.sftp.SFTP_MAX_CHUNK', chunk_size)
    monkeypatch.setattr('pylibsshext.sftp.SFTP_MAX_CHUNK_LIMIT', chunk_size)
    _RemoteFileCounterProxy.instances.clear()
    _RemoteFileCounterProxy.real_cm = sftp_session._open_remote_file_cm
    monkeypatch.setattr(
        sftp_session,
        '_open_remote_file_cm',
        _tracking_remote_file_cm,
    )


@requires_aio_support
@pytest.mark.usefixtures('_small_sftp_limits')
@pytest.mark.parametrize(
    'transmit_payload',
    (SFTP_MAX_CHUNK + 1,),
    ids=('pipelined-payload',),
    indirect=True,
)
def test_get_pipelining(
    dst_path: pathlib.Path,
    sftp_session: SFTP,
    src_path: pathlib.Path,
    transmit_payload: bytes,
) -> None:
    """Check that async SFTP get correctly ramps up, pipelines, and drains across >10 chunks."""
    sftp_session.get(str(src_path), dst_path)
    assert dst_path.read_bytes() == transmit_payload
    assert (
        _RemoteFileCounterProxy.instances[0].io_calls > PIPELINED_CHUNKS_COUNT
    )


@requires_aio_support
@pytest.mark.usefixtures('_small_sftp_limits')
@pytest.mark.parametrize(
    'transmit_payload',
    (SFTP_MAX_CHUNK + 1,),
    ids=('pipelined-payload',),
    indirect=True,
)
def test_put_pipelining(
    dst_path: pathlib.Path,
    sftp_session: SFTP,
    src_path: pathlib.Path,
    transmit_payload: bytes,
) -> None:
    """Check that async SFTP put correctly pipelines and drains across >10 chunks."""
    sftp_session.put(src_path, str(dst_path))
    assert dst_path.read_bytes() == transmit_payload
    assert (
        _RemoteFileCounterProxy.instances[0].io_calls > PIPELINED_CHUNKS_COUNT
    )
