# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name

"""Pytest plugins and fixtures configuration."""

import shutil
import socket
import subprocess
from functools import partial

import pytest
from _service_utils import (  # noqa: WPS436
    ensure_ssh_session_connected, wait_for_svc_ready_state,
)

from pylibsshext.session import Session


_DIR_PRIV_RW_OWNER = 0o700
_FILE_PRIV_RW_OWNER = 0o600


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
    keygen_cmd = (  # noqa: WPS317
        'ssh-keygen',
        '-t', 'rsa',
        '-b', '8192',
        '-C', 'ansible-pylibssh integration tests key',
        '-N', '',
        '-f', str(path),
    )
    subprocess.check_call(keygen_cmd)
    path.chmod(_FILE_PRIV_RW_OWNER)
    return path


@pytest.fixture
def ssh_client_session(ssh_session_connect):
    """Authenticate against SSHD with a private SSH key.

    :yields: Pre-authenticated SSH session.
    :ytype: pylibsshext.session.Session

    # noqa: DAR101
    """
    ssh_session = Session()
    ssh_session_connect(ssh_session)
    try:  # noqa: WPS501
        yield ssh_session
    finally:
        ssh_session.close()
        del ssh_session  # noqa: WPS420


@pytest.fixture
def ssh_session_connect(sshd_addr, ssh_clientkey_path):
    """
    Authenticate existing session object against SSHD with a private SSH key.

    It returns a function that takes session as parameter.

    :returns: Function that will connect the session.
    :rtype: Callback
    """
    return partial(
        ensure_ssh_session_connected,
        sshd_addr=sshd_addr,
        ssh_clientkey_path=ssh_clientkey_path,
    )


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
def sshd_addr(free_port_num, ssh_authorized_keys_path, sshd_hostkey_path, sshd_path, ssh_clientkey_path):
    """Spawn an instance of sshd on a free port.

    :raises RuntimeError: If spawning SSHD failed.

    :yields: SSHD host/port address.
    :ytype: tuple

    # noqa: DAR101
    """
    hostname = '127.0.0.1'
    opt = '-o'
    cmd = (  # noqa: WPS317
        '/usr/sbin/sshd',
        '-D',
        '-f', '/dev/null',
        opt, 'LogLevel=DEBUG3',
        opt, 'HostKey={key!s}'.format(key=sshd_hostkey_path),
        opt, 'PidFile={pid!s}'.format(pid=sshd_path / 'sshd.pid'),

        # NOTE: 'UsePAM no' is not supported on Fedora.
        # Ref: https://bugzilla.redhat.com/show_bug.cgi?id=770756#c1
        opt, 'UsePAM=yes',
        opt, 'PasswordAuthentication=no',
        opt, 'ChallengeResponseAuthentication=no',
        opt, 'GSSAPIAuthentication=no',

        opt, 'StrictModes=no',
        opt, 'PermitEmptyPasswords=yes',
        opt, 'PermitRootLogin=yes',
        opt, 'Protocol=2',
        opt, 'HostbasedAuthentication=no',
        opt, 'IgnoreUserKnownHosts=yes',
        opt, 'Port={port:d}'.format(port=free_port_num),  # port before addr
        opt, 'ListenAddress={host!s}'.format(host=hostname),  # addr after port
        opt, 'AuthorizedKeysFile={auth_keys!s}'.format(auth_keys=ssh_authorized_keys_path),
        opt, 'AcceptEnv=LANG LC_*',
        opt, 'Subsystem=sftp internal-sftp',
    )
    proc = subprocess.Popen(cmd)

    wait_for_svc_ready_state(hostname, free_port_num, ssh_clientkey_path)

    if proc.returncode:
        raise RuntimeError('sshd boom 💣')
    try:  # noqa: WPS501
        yield hostname, free_port_num
    finally:
        proc.terminate()
        proc.wait()
