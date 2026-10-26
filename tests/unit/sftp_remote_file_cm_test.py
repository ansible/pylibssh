"""Tests suite for SFTP _RemoteFile context manager."""

from __future__ import annotations

import os
import random
import re
import typing as _t


if _t.TYPE_CHECKING:
    import pathlib

    from pylibsshext.session import Session


import pytest

from pylibsshext.errors import LibsshSFTPException
from pylibsshext.sftp import SFTP, _RemoteFile


SMALL_PAYLOAD = 32


@pytest.fixture
def sftp_session(ssh_client_session: Session) -> _t.Iterator[SFTP]:
    """Initialize an SFTP session and destroy it after testing."""
    sftp_sess = ssh_client_session.sftp()
    try:  # noqa: WPS501
        yield sftp_sess
    finally:
        sftp_sess.close()
        del sftp_sess  # noqa: WPS420


@pytest.fixture
def dst_path(tmp_path: pathlib.Path) -> pathlib.Path:
    """Return a data destination path."""
    path = tmp_path / 'dst-file.txt'
    assert not path.exists()
    return path


@pytest.fixture
def pre_existing_file_path(tmp_path: pathlib.Path) -> pathlib.Path:
    """Return a path to a pre-existing populated file."""
    path = tmp_path / 'pre-existing-file.txt'
    path.write_bytes(random.randbytes(SMALL_PAYLOAD))
    return path


@pytest.fixture(
    params=(
        pytest.param(
            '\x00{path}',
            id='null-at-start',
        ),
        pytest.param(
            '{path}\x00null',
            id='null-in-middle',
        ),
        pytest.param(
            '{path}\x00',
            id='null-at-end',
        ),
    ),
)
def bogus_null_byte_path(
    request: pytest.FixtureRequest,
    tmp_path: pathlib.Path,
) -> str:
    """Return a bogus remote path containing a null byte in different locations."""
    path_template: str = request.param
    return path_template.format(path=tmp_path / 'bogus-remote-file.txt')


def test_remote_file_rejects_null_byte_path(
    bogus_null_byte_path: str,
    sftp_session: SFTP,
) -> None:
    """Check that _RemoteFile rejects paths with null bytes."""
    error_msg = re.escape(
        f'Invalid remote file path with embedded null byte: {bogus_null_byte_path!r}',
    )
    with pytest.raises(ValueError, match=f'^{error_msg}$'):
        _RemoteFile(
            sftp_obj=sftp_session,
            path=bogus_null_byte_path,
            flags=os.O_RDONLY,
        )


def test_remote_file_write_failure(
    pre_existing_file_path: pathlib.Path,
    sftp_session: SFTP,
) -> None:
    """Check that calling write() on a read-only _RemoteFile raises LibsshSFTPException."""
    with _RemoteFile(
        sftp_obj=sftp_session,
        path=str(pre_existing_file_path),
        flags=os.O_RDONLY,
    ) as remote_fd:
        error_msg = re.escape(
            f'Writing to remote file [{pre_existing_file_path!s}] failed with error',
        )
        with pytest.raises(LibsshSFTPException, match=rf'^{error_msg} \['):
            remote_fd.write(bytearray(b'unauthorized payload'))


@pytest.mark.parametrize(
    'payload',
    (
        b'bytes-payload',
        bytearray(b'bytearray-payload'),
        memoryview(b'memoryview-payload'),
    ),
    ids=lambda payload: type(payload).__name__,
)
def test_remote_file_write_buffers(
    dst_path: pathlib.Path,
    payload: bytes | bytearray | memoryview,
    sftp_session: SFTP,
) -> None:
    """Check that _RemoteFile.write() accepts various buffer protocol types."""
    with _RemoteFile(
        sftp_obj=sftp_session,
        path=str(dst_path),
        flags=os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
    ) as remote_fd:
        written = remote_fd.write(payload)
        assert written == len(payload)
    assert dst_path.read_bytes() == bytes(payload)


def test_remote_file_write_empty(
    dst_path: pathlib.Path,
    sftp_session: SFTP,
) -> None:
    """Check that _RemoteFile.write() handles empty buffers cleanly."""
    with _RemoteFile(
        sftp_obj=sftp_session,
        path=str(dst_path),
        flags=os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
    ) as remote_fd:
        assert remote_fd.write(b'') == 0
    assert dst_path.read_bytes() == b''


def test_remote_file_read_failure(
    dst_path: pathlib.Path,
    sftp_session: SFTP,
) -> None:
    """Check that calling readinto() on a write-only _RemoteFile raises LibsshSFTPException."""
    with _RemoteFile(
        sftp_obj=sftp_session,
        path=str(dst_path),
        flags=os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
    ) as remote_fd:
        read_buffer = bytearray(SMALL_PAYLOAD)
        error_msg = re.escape(
            f'Reading data from remote file [{dst_path!s}] failed with error',
        )
        with pytest.raises(LibsshSFTPException, match=rf'^{error_msg} \['):
            remote_fd.readinto(read_buffer)


class _SentinelError(RuntimeError):
    """Sentinel error for testing exception propagation."""


def _choke_on_remote_file(
    *,
    sftp_obj: SFTP,
    path: pathlib.Path,
    flags: int,
) -> _t.NoReturn:
    """Ensure exceptions raised from within CM are propagated."""
    with _RemoteFile(
        sftp_obj=sftp_obj,
        path=str(path),
        flags=flags,
    ):
        msg = 'boom'
        raise _SentinelError(msg)


def test_remote_file_cm_reraises_cleans_up(
    pre_existing_file_path: pathlib.Path,
    sftp_session: SFTP,
) -> None:
    """Ensure ``__exit__()`` propagates exceptions."""
    with pytest.raises(_SentinelError, match=r'^boom$'):
        _choke_on_remote_file(
            sftp_obj=sftp_session,
            path=pre_existing_file_path,
            flags=os.O_RDONLY,
        )
