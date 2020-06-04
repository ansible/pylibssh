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

from cpython.bytes cimport PyBytes_AS_STRING
from posix.fcntl cimport O_WRONLY, O_CREAT, O_TRUNC, O_RDONLY

from pylibsshext.session cimport get_libssh_session
from pylibsshext.errors cimport LibsshSFTPException


MSG_MAP = {
    sftp.SSH_FX_OK: "No error",
    sftp.SSH_FX_EOF: "End-of-file encountered",
    sftp.SSH_FX_NO_SUCH_FILE: "File doesn't exist",
    sftp.SSH_FX_PERMISSION_DENIED: "Permission denied",
    sftp.SSH_FX_FAILURE: "Generic failure",
    sftp.SSH_FX_BAD_MESSAGE: "Garbage received from server",
    sftp.SSH_FX_NO_CONNECTION: "No connection has been set up",
    sftp.SSH_FX_CONNECTION_LOST: "There was a connection, but we lost it",
    sftp.SSH_FX_OP_UNSUPPORTED: "Operation not supported by the server",
    sftp.SSH_FX_INVALID_HANDLE: "Invalid file handle",
    sftp.SSH_FX_NO_SUCH_PATH: "No such file or directory path exists",
    sftp.SSH_FX_FILE_ALREADY_EXISTS: "An attempt to create an already existing file or directory has been made",
    sftp.SSH_FX_WRITE_PROTECT: "We are trying to write on a write-protected filesystem",
    sftp.SSH_FX_NO_MEDIA: "No media in remote drive"
}
cdef class SFTP:
    def __cinit__(self, session):
        self.session = session
        self._libssh_sftp_session = sftp.sftp_new(get_libssh_session(session))
        if self._libssh_sftp_session is NULL:
            raise LibsshSFTPException("Failed to create new session")
        if sftp.sftp_init(self._libssh_sftp_session) != libssh.SSH_OK:
            raise LibsshSFTPException("Error initializing SFTP session")

    def __dealloc__(self):
        if self._libssh_sftp_session is not NULL:
            sftp.sftp_free(self._libssh_sftp_session)
            self._libssh_sftp_session = NULL

    def put(self, local_file, remote_file):
        cdef sftp.sftp_file rf
        with open(local_file, "rb") as f:
            remote_file_b = remote_file
            if isinstance(remote_file_b, unicode):
                remote_file_b = remote_file.encode("utf-8")

            rf = sftp.sftp_open(self._libssh_sftp_session, remote_file_b, O_WRONLY | O_CREAT | O_TRUNC, sftp.S_IRWXU)
            if rf is NULL:
                raise LibsshSFTPException("Opening remote file [%s] for write failed with error [%s]" % (remote_file, MSG_MAP.get(self._get_sftp_error_str())))
            buffer = f.read(1024)

            while buffer != b"":
                length = len(buffer)
                written = sftp.sftp_write(rf, PyBytes_AS_STRING(buffer), length)
                if written != length:
                    sftp.sftp_close(rf)
                    raise LibsshSFTPException("Writing to remote file [%s] failed" % remote_file)
                buffer = f.read(1024)
            sftp.sftp_close(rf)

    def get(self, remote_file, local_file):
        cdef sftp.sftp_file rf
        cdef char read_buffer[1024]

        remote_file_b = remote_file
        if isinstance(remote_file_b, unicode):
            remote_file_b = remote_file.encode("utf-8")

        rf = sftp.sftp_open(self._libssh_sftp_session, remote_file_b, O_RDONLY, sftp.S_IRWXU)
        if rf is NULL:
            raise LibsshSFTPException("Opening remote file [%s] for read failed with error [%s]" % (remote_file, MSG_MAP.get(self._get_sftp_error_str())))

        while True:
            file_data = sftp.sftp_read(rf, <void *>read_buffer, sizeof(char) * 1024)
            if file_data == 0:
                break
            elif file_data < 0:
                sftp.sftp_close(rf)
                raise LibsshSFTPException("Reading data from remote file [%s] failed with error [%s]"
                                          % (remote_file, MSG_MAP.get(self._get_sftp_error_str())))

            with open(local_file, 'w+') as f:
                bytes_wrote = f.write(read_buffer[:file_data].decode('utf-8'))
                if bytes_wrote and file_data != bytes_wrote:
                    sftp.sftp_close(rf)
                    raise LibsshSFTPException("Number of bytes [%s] read from remote file [%s]"
                                              " does not match number of bytes [%s] written to local file [%s]"
                                              " due to error [%s]"
                                              % (file_data, remote_file, bytes_wrote, local_file, MSG_MAP.get(self._get_sftp_error_str())))
        sftp.sftp_close(rf)

    def close(self):
        if self._libssh_sftp_session is not NULL:
            sftp.sftp_free(self._libssh_sftp_session)
            self._libssh_sftp_session = NULL

    def _get_sftp_error_str(self):
        return sftp.sftp_get_error(self._libssh_sftp_session)
