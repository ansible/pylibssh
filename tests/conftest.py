# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name

"""Pytest plugins and fixtures configuration."""

import shutil
import socket
import subprocess
import time

import pytest

_DIR_PRIV_RW_OWNER = 0o700
_FILE_PRIV_RW_OWNER = 0o600
_SSHD_SPAWN_TIME = 0.009


@pytest.fixture
def free_port_num():
    """Detect a free port number using a temporary ephemeral port.

    :returns: An unoccupied port number.
    :rtype: int

    # noqa: 401
    """
    # NOTE: It should work most of the time except for the races.
    # This technique is suboptimal because we temporary occupy the port
    # and then close the socket. So there's a small time slot between
    # us closing the port and sshd trying to listen to it when some
    # other process can intercept it. Ideally, sshd should rely on an
    # ephemeral port but it doesn't support Port=0. I tried to work
    # around this by emulating socket activation mode but
    # unsuccessfully so far.
    sock = socket.socket(socket.AF_INET)

    try:
        sock.bind(('127.0.0.1', 0))
    except socket.error:
        sock.close()
        raise

    try:  # noqa: WPS501
        return sock.getsockname()[1]
    finally:
        sock.close()


@pytest.fixture
def sshd_path(tmp_path):
    """Create a tmp dir for sshd.

    :return: Temporary SSH dir path.
    :rtype: pathlib.Path

    # noqa: DAR101
    """
    path = tmp_path / 'sshd'
    path.mkdir()
    path.chmod(_DIR_PRIV_RW_OWNER)
    return path


@pytest.fixture
def sshd_hostkey_path(sshd_path):
    """Generate a keypair for SSHD.

    :return: Private key path for SSHD server.
    :rtype: pathlib.Path

    # noqa: DAR101
    """
    path = sshd_path / 'ssh_host_rsa_key'
    keygen_cmd = 'ssh-keygen', '-N', '', '-f', str(path)
    subprocess.check_call(keygen_cmd)
    path.chmod(_FILE_PRIV_RW_OWNER)
    return path


@pytest.fixture
def ssh_clientkey_path(sshd_path):
    """Generate an SSH keypair.

    :return: Private SSH key path.
    :rtype: pathlib.Path

    # noqa: DAR101
    """
    path = sshd_path / 'ssh_client_rsa_key'
    keygen_cmd = 'ssh-keygen', '-N', '', '-f', str(path)
    subprocess.check_call(keygen_cmd)
    path.chmod(_FILE_PRIV_RW_OWNER)
    return path


@pytest.fixture
def ssh_authorized_keys_path(sshd_path, ssh_clientkey_path):
    """Populate authorized_keys.

    :return: `authorized_keys` file path.
    :rtype: pathlib.Path

    # noqa: DAR101
    """
    path = sshd_path / 'authorized_keys'
    public_key_path = ssh_clientkey_path.with_suffix('.pub')
    shutil.copyfile(str(public_key_path), str(path))
    path.chmod(_FILE_PRIV_RW_OWNER)
    return path


@pytest.fixture
def sshd_addr(free_port_num, ssh_authorized_keys_path, sshd_hostkey_path, sshd_path):
    """Spawn an instance of sshd on a free port.

    :raises RuntimeError: If spawning SSHD failed.

    :yields: SSHD host/port address.
    :ytype: tuple

    # noqa: DAR101
    """
    opt = '-o'
    cmd = (  # noqa: WPS317
        '/usr/sbin/sshd',
        '-D', '-ddd',
        '-f', '/dev/null',
        opt, 'HostKey={key!s}'.format(key=sshd_hostkey_path),
        opt, 'PidFile={pid!s}'.format(pid=sshd_path / 'sshd.pid'),
        opt, 'UsePAM=no',
        opt, 'StrictModes=no',
        opt, 'PermitEmptyPasswords=yes',
        opt, 'PermitRootLogin=yes',
        opt, 'Protocol=2',
        opt, 'HostbasedAuthentication=no',
        opt, 'IgnoreUserKnownHosts=yes',
        opt, 'ListenAddress=127.0.0.1',
        opt, 'AuthorizedKeysFile={auth_keys!s}'.format(auth_keys=ssh_authorized_keys_path),
        opt, 'AcceptEnv=LANG LC_*',
        opt, 'Subsystem=sftp internal-sftp',
        opt, 'Port={port:d}'.format(port=free_port_num),
    )
    proc = subprocess.Popen(cmd)  # , stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(_SSHD_SPAWN_TIME)
    if proc.returncode:
        raise RuntimeError('sshd boom')
    try:  # noqa: WPS501
        yield '127.0.0.1', free_port_num
    finally:
        proc.terminate()
        proc.wait()
