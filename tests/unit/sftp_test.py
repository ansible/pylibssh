# -*- coding: utf-8 -*-

"""Tests suite for sftp."""

import uuid

import pytest


@pytest.fixture
def sftp_session(ssh_client_session):
    """Initialize an SFTP session and destroy it after testing."""
    sftp_sess = ssh_client_session.sftp()
    try:  # noqa: WPS501
        yield sftp_sess
    finally:
        sftp_sess.close()
        del sftp_sess  # noqa: WPS420


@pytest.fixture
def transmit_payload():
    """Generate a binary test payload."""
    uuid_name = uuid.uuid4()
    return 'Hello, {name!s}'.format(name=uuid_name).encode()


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
