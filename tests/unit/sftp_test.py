# -*- coding: utf-8 -*-

"""Tests suite for sftp."""


def test_make_sftp(ssh_client_session):
    """Smoke-test SFTP instance creation."""
    assert ssh_client_session.sftp()
