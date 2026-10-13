"""Tests suite for scp."""

import os
import pathlib
import random
import typing as _t  # noqa: WPS111

import pytest

from pylibsshext.errors import LibsshSCPException
from pylibsshext.scp import SCP, SCP_MAX_CHUNK
from pylibsshext.session import Session


@pytest.fixture
def ssh_scp(ssh_client_session: Session) -> _t.Iterator[SCP]:
    """Initialize an SCP session and destroy it after testing."""
    scp = ssh_client_session.scp()
    try:  # noqa: WPS501
        yield scp
    finally:
        del scp  # noqa: WPS420


@pytest.fixture(
    params=(32, SCP_MAX_CHUNK + 1),
    ids=('small-payload', 'large-payload'),
)
def transmit_payload(request: pytest.FixtureRequest) -> bytes:
    """Generate a binary test payload.

    The choice 32 is arbitrary small value.

    The choice SCP_CHUNK_SIZE + 1 (64kB + 1B) is meant to be 1B larger than the chunk
    size used in :file:`scp.pyx` to make sure we exercise at least two rounds of
    reading/writing.
    """
    payload_len = request.param
    assert isinstance(payload_len, int)
    return random.randbytes(payload_len)


@pytest.fixture
def file_paths_pair(
    tmp_path: pathlib.Path,
    transmit_payload: bytes,
) -> tuple[pathlib.Path, pathlib.Path]:
    """Populate a source file and make a destination path."""
    src_path = tmp_path / 'src-file.txt'
    dst_path = tmp_path / 'dst-file.txt'
    src_path.write_bytes(transmit_payload)
    return src_path, dst_path


@pytest.fixture
def src_path(
    file_paths_pair: tuple[pathlib.Path, pathlib.Path],
) -> pathlib.Path:
    """Return a data source path."""
    return file_paths_pair[0]


@pytest.fixture
def dst_path(
    file_paths_pair: tuple[pathlib.Path, pathlib.Path],
) -> pathlib.Path:
    """Return a data destination path."""
    path = file_paths_pair[1]
    assert not path.exists()
    return path


def test_put(
    dst_path: pathlib.Path,
    src_path: pathlib.Path,
    ssh_scp: SCP,
    transmit_payload: bytes,
) -> None:
    """Check that SCP file transfer works."""
    ssh_scp.put(str(src_path), str(dst_path))
    assert dst_path.read_bytes() == transmit_payload


def test_get(
    dst_path: pathlib.Path,
    src_path: pathlib.Path,
    ssh_scp: SCP,
    transmit_payload: bytes,
) -> None:
    """Check that SCP file download works."""
    ssh_scp.get(str(src_path), str(dst_path))
    assert dst_path.read_bytes() == transmit_payload


@pytest.fixture
def path_to_non_existent_src_file(tmp_path: pathlib.Path) -> pathlib.Path:
    """Return a remote path that does not exist."""
    path = tmp_path / 'non-existing.txt'
    assert not path.exists()
    return path


def test_copy_from_non_existent_remote_path(
    path_to_non_existent_src_file: pathlib.Path,
    ssh_scp: SCP,
) -> None:
    """Check that SCP file download raises exception if the remote file is missing."""
    error_msg = '^Error receiving information about file:'
    with pytest.raises(LibsshSCPException, match=error_msg):
        ssh_scp.get(str(path_to_non_existent_src_file), os.devnull)


@pytest.fixture
def pre_existing_file_path(tmp_path: pathlib.Path) -> pathlib.Path:
    """Return local path for a pre-populated file."""
    path = tmp_path / 'pre-existing-file.txt'
    path.write_bytes(b'whatever')
    return path


def test_get_existing_local(
    pre_existing_file_path: pathlib.Path,
    src_path: pathlib.Path,
    ssh_scp: SCP,
    transmit_payload: bytes,
) -> None:
    """Check that SCP file download works and overwrites local file if it exists."""
    ssh_scp.get(str(src_path), str(pre_existing_file_path))
    assert pre_existing_file_path.read_bytes() == transmit_payload
