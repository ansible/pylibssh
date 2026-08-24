"""Tests suite for sftp."""

import random
import uuid

import pytest

from pylibsshext.errors import LibsshSFTPException

from pylibsshext import __libssh_version__, sftp


SMALL_PAYLOAD = 32
HUGE_CHUNK = 1024 * 1024


@pytest.fixture
def sftp_session(ssh_client_session):
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
            sftp.SFTP_MAX_CHUNK + 1,
            id='large-payload',
        ),
        pytest.param(
            # 1B larger than any limits advertised by SFTP servers
            # passing this directly on wire will not be handled by server
            HUGE_CHUNK + 1,
            id='huge-payload',
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


def test_put_existing(
    pre_existing_dst_path,
    src_path,
    sftp_session,
    transmit_payload,
):
    """Check that SFTP file upload works when target file exists."""
    sftp_session.put(str(src_path), str(pre_existing_dst_path))
    assert pre_existing_dst_path.read_bytes() == transmit_payload


LIBSSH_VERSION_TUPLE = tuple(map(int, __libssh_version__.split('.')))
xfail_on_libssh_below0_11_as_crashing = pytest.mark.xfail(
    LIBSSH_VERSION_TUPLE < (0, 11, 0),
    reason='libssh < 0.11.0 does not partition large writes.',
    strict=True,
    raises=LibsshSFTPException,
)


@xfail_on_libssh_below0_11_as_crashing  # pragma: no cover
@pytest.mark.parametrize(
    'transmit_payload',
    (HUGE_CHUNK + 1,),
    indirect=True,
    ids=('huge-payload',),
)
def test_put_chunk_partition(
    dst_path,
    src_path,
    sftp_session,
    transmit_payload,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Check the large write is split into chunks by libssh."""
    monkeypatch.setattr(sftp, 'SFTP_MAX_CHUNK', HUGE_CHUNK)
    sftp_session.put(str(src_path), str(dst_path))
    assert dst_path.read_bytes() == transmit_payload
