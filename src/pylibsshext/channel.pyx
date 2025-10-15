#
# This file is part of the pylibssh library
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, see file LICENSE.rst in this
# repository.
#
import signal
import time
from io import BytesIO

from cpython.bytes cimport PyBytes_AS_STRING
from libc.string cimport memset

from pylibsshext.errors cimport LibsshChannelException
from pylibsshext.errors import LibsshChannelReadFailure
from pylibsshext.session cimport get_libssh_session, get_session_retries

from subprocess import CompletedProcess


cdef int _process_outputs(libssh.ssh_session session,
                          libssh.ssh_channel channel,
                          void *data,
                          libssh.uint32_t len,
                          int is_stderr,
                          void *userdata) with gil:
    if len == 0:
        return 0
    data_b = <bytes>(<char *>data)[:len]
    result = <object>userdata
    if is_stderr:
        result.stderr += data_b
    else:
        result.stdout += data_b
    return len

cdef class ChannelCallback:
    def __cinit__(self):
        memset(&self.callback, 0, sizeof(self.callback))
        callbacks.ssh_callbacks_init(&self.callback)
        self.callback.channel_data_function = <callbacks.ssh_channel_data_callback>&_process_outputs

    def set_user_data(self, userdata):
        self._userdata = userdata
        self.callback.userdata = <void *>self._userdata

cdef class Channel:
    def __cinit__(self, session):
        self._session = session
        self._libssh_session = get_libssh_session(session)
        self._libssh_channel = libssh.ssh_channel_new(self._libssh_session)

        if self._libssh_channel is NULL:
            raise MemoryError

        self._open_session_with_retries(self._libssh_channel)

    def __dealloc__(self):
        if self._libssh_channel is not NULL:
            libssh.ssh_channel_close(self._libssh_channel)
            libssh.ssh_channel_free(self._libssh_channel)
            self._libssh_channel = NULL

    def request_shell(self):
        self.request_pty()
        rc = libssh.ssh_channel_request_shell(self._libssh_channel)
        if rc != libssh.SSH_OK:
            raise LibsshChannelException("Failed to request_shell: [%d]" % rc)

    def request_exec(self, command):
        """Run a shell command without an interactive shell."""
        rc = libssh.ssh_channel_request_exec(self._libssh_channel, command.encode("utf-8"))
        if rc != libssh.SSH_OK:
            raise LibsshChannelException("Failed to request_exec: [%d]" % rc)

    def request_pty(self):
        rc = libssh.ssh_channel_request_pty(self._libssh_channel)
        if rc != libssh.SSH_OK:
            raise LibsshChannelException("Failed to request pty: [%d]" % rc)

    def request_pty_size(self, terminal, col, row):
        rc = libssh.ssh_channel_request_pty_size(self._libssh_channel, terminal, col, row)
        if rc != libssh.SSH_OK:
            raise LibsshChannelException("Failed to request pty with [%d] for terminal [%s], "
                                         "columns [%d] and rows [%d]" % (rc, terminal, col, row))
        rc = libssh.ssh_channel_request_shell(self._libssh_channel)
        if rc != libssh.SSH_OK:
            raise LibsshChannelException("Failed to request_shell: [%d]" % rc)

    def poll(self, timeout=-1, stderr=0):
        if timeout < 0:
            rc = libssh.ssh_channel_poll(self._libssh_channel, stderr)
        else:
            rc = libssh.ssh_channel_poll_timeout(self._libssh_channel, timeout, stderr)
        if rc == libssh.SSH_ERROR:
            raise LibsshChannelException("Failed to poll channel: [{0}]".format(rc))
        return rc

    def read_nonblocking(self, size=1024, stderr=0):
        cdef char buffer[1024]
        size_m = size
        if size_m > sizeof(buffer):
            size_m = sizeof(buffer)
        nbytes = libssh.ssh_channel_read_nonblocking(self._libssh_channel, buffer, size_m, stderr)
        if nbytes == libssh.SSH_ERROR:
            # This is what Session._get_session_error_str() does, but we don't have the Python object
            error = libssh.ssh_get_error(<void*>self._libssh_session).decode()
            raise LibsshChannelReadFailure(error)
        elif nbytes == libssh.SSH_EOF:
            return None

        return <bytes>buffer[:nbytes]

    def recv(self, size=1024, stderr=0):
        return self.read_nonblocking(size=size, stderr=stderr)

    def write(self, data):
        written = libssh.ssh_channel_write(self._libssh_channel, PyBytes_AS_STRING(data), len(data))
        if written == libssh.SSH_ERROR:
            raise LibsshChannelException("Failed to write to ssh channel")
        return written

    def sendall(self, data):
        return self.write(data)

    def read_bulk_response(self, stderr=0, timeout=0.001, retry=5):
        if retry <= 0:
            raise ValueError(
                'Got arg `retry={arg!r}` but it must be greater than 0'.
                format(arg=retry),
            )

        response = b""
        with BytesIO() as recv_buff:
            for _ in range(retry, 0, -1):
                data = self.read_nonblocking(size=1024, stderr=stderr)
                if not data:
                    if timeout:
                        time.sleep(timeout)
                    continue

                recv_buff.write(data)
            response = recv_buff.getvalue()
        return response

    cdef _open_session_with_retries(self, libssh.ssh_channel channel):
        retry = get_session_retries(self._session)

        for attempt in range(retry + 1):
            rc = libssh.ssh_channel_open_session(channel)
            if rc == libssh.SSH_OK:
                break
            if rc == libssh.SSH_AGAIN and attempt < retry:
                continue
            # either SSH_ERROR, or SSH_AGAIN with final attempt
            if rc != libssh.SSH_OK:
                self._libssh_channel = NULL
                libssh.ssh_channel_free(channel)
                raise LibsshChannelException(f"Failed to open_session: [{rc}]")

    def exec_command(self, command):
        # request_exec requires a fresh channel each run, so do not use the existing channel
        cdef libssh.ssh_channel channel = libssh.ssh_channel_new(self._libssh_session)
        if channel is NULL:
            raise MemoryError

        self._open_session_with_retries(channel)

        result = CompletedProcess(args=command, returncode=-1, stdout=b'', stderr=b'')

        cb = ChannelCallback()
        cb.set_user_data(result)
        callbacks.ssh_set_channel_callbacks(channel, &cb.callback)
        # keep the callback around in the session object to avoid use after free
        self._session.push_callback(cb)

        rc = libssh.ssh_channel_request_exec(channel, command.encode("utf-8"))
        if rc != libssh.SSH_OK:
            libssh.ssh_channel_close(channel)
            libssh.ssh_channel_free(channel)
            raise LibsshChannelException("Failed to execute command [{0}]: [{1}]".format(command, rc))

        # wait before remote writes all data before closing the channel
        while not libssh.ssh_channel_is_eof(channel):
            libssh.ssh_channel_poll(channel, 0)

        libssh.ssh_channel_send_eof(channel)
        result.returncode = libssh.ssh_channel_get_exit_status(channel)
        if channel is not NULL:
            libssh.ssh_channel_close(channel)
            libssh.ssh_channel_free(channel)

        return result

    def send_eof(self):
        """Send EOF to the channel, this will close stdin."""
        rc = libssh.ssh_channel_send_eof(self._libssh_channel)
        if rc != libssh.SSH_OK:
            raise LibsshChannelException("Failed to ssh_channel_send_eof: [%d]" % rc)

    def send_signal(self, sig):
        """
        Send signal to the remote process.

        :param sig: a signal constant from ``signal``, e.g. ``signal.SIGUSR1``.
        :type sig: signal.Signals
        """
        if not isinstance(sig, signal.Signals):
            raise TypeError(f"Expecting signal.Signals not {type(sig)}")

        sshsig = sig.name.removeprefix("SIG")
        rc = libssh.ssh_channel_request_send_signal(self._libssh_channel, sshsig.encode("utf-8"))
        if rc != libssh.SSH_OK:
            raise LibsshChannelException("Failed to ssh_channel_request_send_signal: [%d]" % rc)

    def get_channel_exit_status(self):
        return libssh.ssh_channel_get_exit_status(self._libssh_channel)

    @property
    def is_eof(self):
        """True if remote has sent an EOF."""
        rc = libssh.ssh_channel_is_eof(self._libssh_channel)
        return rc != 0

    def close(self):
        if self._libssh_channel is not NULL:
            libssh.ssh_channel_close(self._libssh_channel)
            libssh.ssh_channel_free(self._libssh_channel)
            self._libssh_channel = NULL
