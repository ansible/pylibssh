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
from libc.string cimport memset
from cpython.bytes cimport PyBytes_AS_STRING

from pylibssh.session cimport get_libssh_session
from pylibssh.errors cimport LibsshChannelException
from subprocess import CalledProcessError, CompletedProcess


cdef int _process_outputs(libssh.ssh_session session,
                          libssh.ssh_channel channel,
                          void *data,
                          libssh.uint32_t len,
                          int is_stderr,
                          void *userdata):
    if len == 0:
        return 0
    data_b = <bytes>(<char *>data)[:len]
    result = <object>userdata
    if is_stderr:
        result.stderr += data_b
    else:
        result.stdout += data_b
    return len

cdef class Channel:
    def __cinit__(self, session):
        self._libssh_session = get_libssh_session(session)
        self._libssh_channel = libssh.ssh_channel_new(self._libssh_session)
        if self._libssh_channel is NULL:
            raise MemoryError
        rc = libssh.ssh_channel_open_session(self._libssh_channel)
        if rc != libssh.SSH_OK:
            self._libssh_channel = NULL
            libssh.ssh_channel_free(self._libssh_channel)
            raise LibsshChannelException("Failed to open_session: [%d]" % rc)

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
            if rc == libssh.SSH_ERROR:
                raise LibsshChannelException("Failed to poll channel: [%d]" % rc)
        else:
            rc = libssh.ssh_channel_poll_timeout(self._libssh_channel, timeout, stderr)
            if rc == libssh.SSH_ERROR:
                raise LibsshChannelException("Failed to poll channel: [%d]" % rc)
        return rc

    def read_nonblocking(self, size=1024, stderr=0):
        cdef char buffer[1024]
        size_m = size
        if size_m > sizeof(buffer):
            size_m = sizeof(buffer)
        nbytes = libssh.ssh_channel_read_nonblocking(self._libssh_channel, buffer, size_m, stderr)
        return <bytes>buffer[:nbytes]

    def recv(self, size=1024, stderr=0):
        return self.read_nonblocking(size=size, stderr=stderr)

    def write(self, data):
        return libssh.ssh_channel_write(self._libssh_channel, PyBytes_AS_STRING(data), len(data))

    def sendall(self, data):
        return self.write(data)

    def exec_command(self, command):
        cdef libssh.ssh_channel channel = libssh.ssh_channel_new(self._libssh_session)
        if channel is NULL:
            raise MemoryError
        rc = libssh.ssh_channel_open_session(channel)
        if rc != libssh.SSH_OK:
            libssh.ssh_channel_free(channel)
            raise CalledProcessError()

        rc = libssh.ssh_channel_request_exec(channel, command.encode("utf-8"))
        if rc != libssh.SSH_OK:
            libssh.ssh_channel_close(channel)
            libssh.ssh_channel_free(channel)
            raise CalledProcessError()

        cdef callbacks.ssh_channel_callbacks_struct cb
        memset(&cb, 0, sizeof(cb))
        cb.channel_data_function = <callbacks.ssh_channel_data_callback>&_process_outputs
        result = CompletedProcess(args=command, returncode=-1, stdout=b'', stderr=b'')
        cb.userdata = <void *>result
        callbacks.ssh_callbacks_init(&cb)
        callbacks.ssh_set_channel_callbacks(channel, &cb)

        libssh.ssh_channel_send_eof(channel)
        result.returncode = libssh.ssh_channel_get_exit_status(channel)

        libssh.ssh_channel_close(channel)
        libssh.ssh_channel_free(channel)

        return result

    def get_channel_exit_status(self):
        return libssh.ssh_channel_get_exit_status(self._libssh_channel)

    def close(self):
        if self._libssh_channel is not NULL:
            libssh.ssh_channel_close(self._libssh_channel)
        libssh.ssh_channel_free(self._libssh_channel)
        self._libssh_channel = NULL
