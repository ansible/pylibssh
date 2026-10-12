"""Tests suite for sftp."""

import os
import random
import uuid

import pytest

from pylibsshext.errors import LibsshSFTPException
from pylibsshext.sftp import SFTP, SFTP_MAX_CHUNK


SMALL_PAYLOAD = 32


@pytest.fixture
def sftp_session(ssh_client_session) -> SFTP:
    """Initialize an SFTP session and destroy it after testing."""
    sftp_sess = ssh_client_session.sftp()
    try:  # noqa: WPS501
        yield sftp_sess
    finally:
        sftp_sess.close()
        del sftp_sess  # noqa: WPS420


@pytest.fixture(
    params=(
        pytest.param(
            0,  # empty file
            id='empty-payload',
        ),
        pytest.param(
            SMALL_PAYLOAD,  # arbitrary small value
            id='small-payload',
        ),
        pytest.param(
            # 1B larger than chunk size in sftp to make sure we exercise
            # at least two rounds of reading/writing
            SFTP_MAX_CHUNK + 1,
            id='large-payload',
        ),
    ),
)
def transmit_payload(request: pytest.FixtureRequest) -> bytes:
    """Generate binary test payloads of assorted sizes."""
    payload_len = request.param
    assert isinstance(payload_len, int)
    return random.randbytes(payload_len)


@pytest.fixture
def file_paths_pair(tmp_path, transmit_payload):
    """Populate a source file and make a destination path."""
    src_path = tmp_path / 'src-file.txt'
    dst_path = tmp_path / 'dst-file.txt'
    src_path.write_bytes(transmit_payload)
    return src_path, dst_path


@pytest.fixture
def src_path(file_paths_pair):
    """Return a data source path."""
    return file_paths_pair[0]


@pytest.fixture
def dst_path(file_paths_pair):
    """Return a data destination path."""
    path = file_paths_pair[1]
    assert not path.exists()
    return path


@pytest.fixture
def other_payload():
    """Generate a binary test payload."""
    uuid_name = uuid.uuid4()
    return f'Original content: {uuid_name!s}'.encode()


@pytest.fixture
def pre_existing_dst_path(dst_path, other_payload):
    """Return a data destination path."""
    dst_path.write_bytes(other_payload)
    assert dst_path.exists()
    return dst_path


def test_make_sftp(sftp_session):
    """Smoke-test SFTP instance creation."""
    assert sftp_session


def test_put(dst_path, src_path, sftp_session, transmit_payload):
    """Check that SFTP file transfer works."""
    sftp_session.put(str(src_path), str(dst_path))
    assert dst_path.read_bytes() == transmit_payload


def test_get(dst_path, src_path, sftp_session, transmit_payload):
    """Check that SFTP file download works."""
    sftp_session.get(str(src_path), str(dst_path))
    assert dst_path.read_bytes() == transmit_payload


def test_get_existing(
    pre_existing_dst_path,
    src_path,
    sftp_session,
    transmit_payload,
):
    """Check that SFTP file download works when target file exists."""
    sftp_session.get(str(src_path), str(pre_existing_dst_path))
    assert pre_existing_dst_path.read_bytes() == transmit_payload


def test_sftp_version(sftp_session):
    """Check that SFTP protocol version (reported by OpenSSH server) is 3."""
    assert sftp_session.version == 3


def test_put_existing(
    pre_existing_dst_path,
    src_path,
    sftp_session,
    transmit_payload,
):
    """Check that SFTP file upload works when target file exists."""
    sftp_session.put(str(src_path), str(pre_existing_dst_path))
    assert pre_existing_dst_path.read_bytes() == transmit_payload


@pytest.fixture
def existing_path(tmp_path, transmit_payload):
    """Return a file path that exist and has given size."""
    path = tmp_path / 'test-file.txt'
    path.write_bytes(transmit_payload)
    return path


def test_stat_existing(  # noqa: WPS218
    existing_path: os.PathLike,
    transmit_payload: bytes,
    sftp_session: SFTP,
):
    """Check the stat returns the right file information."""
    si = existing_path.stat()

    attrs = sftp_session.stat(str(existing_path))
    assert attrs.size == len(transmit_payload)
    assert attrs.size == si.st_size
    assert attrs.mtime == int(si.st_mtime)
    assert attrs.atime == int(si.st_atime)
    assert attrs.permissions == si.st_mode
    assert attrs.uid == si.st_uid
    assert attrs.gid == si.st_gid

    # file type
    assert attrs.is_regular
    props = ('is_dir', 'is_symlink', 'is_special', 'is_unknown')
    for prop in props:
        assert not getattr(attrs, prop)


# These will work only with other operation than stat
@pytest.mark.parametrize(
    'attribute',
    (
        'name',
        'longname',
        'owner',
        'group',
    ),
)
def test_stat_unsupported(
    existing_path: os.PathLike,
    sftp_session: SFTP,
    attribute: str,
) -> None:
    """Check the unsupported attributes are reported correctly."""
    msg = rf'^The attribute {attribute} is not available$'
    attrs = sftp_session.stat(existing_path)
    with pytest.raises(LookupError, match=msg):
        getattr(attrs, attribute)


def test_stat_bytes(
    existing_path: os.PathLike,
    sftp_session: SFTP,
) -> None:
    """Check the unsupported attributes are reported correctly."""
    error_msg = r'^Expected str or os.PathLike, got bytes$'
    path_b = str(existing_path).encode('utf-8')
    with pytest.raises(TypeError, match=error_msg):
        sftp_session.stat(path_b)


@pytest.fixture
def non_existing_path(tmp_path) -> os.PathLike:
    """Return a path that is guaranteed to not exist."""
    return tmp_path / 'no-file-here.txt'


def test_stat_non_existing(
    non_existing_path: os.PathLike,
    sftp_session: SFTP,
) -> None:
    """Check the stat raises exception on non-existing file."""
    error_msg = rf'^Failed to stat the remote file \[{non_existing_path}\]. Error: \[File doesn\'t exist\]$'
    with pytest.raises(LibsshSFTPException, match=error_msg):
        sftp_session.stat(non_existing_path)
    with pytest.raises(LibsshSFTPException, match=error_msg):
        sftp_session.stat(str(non_existing_path))
