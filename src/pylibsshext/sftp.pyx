#
# This file is part of the ansible-pylibssh library
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

from posix.fcntl cimport O_CREAT, O_RDONLY, O_TRUNC, O_WRONLY

from cpython.bytes cimport PyBytes_AS_STRING
from cpython.mem cimport PyMem_Free, PyMem_Malloc

from pylibsshext.errors cimport LibsshSFTPException
from pylibsshext.session cimport get_libssh_session


SFTP_MAX_CHUNK = 32_768  # 32kB


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
                raise LibsshSFTPException("Opening remote file [%s] for write failed with error [%s]" % (remote_file, self._get_sftp_error_str()))
            buffer = f.read(SFTP_MAX_CHUNK)

            while buffer != b"":
                length = len(buffer)
                written = sftp.sftp_write(rf, PyBytes_AS_STRING(buffer), length)
                if written != length:
                    sftp.sftp_close(rf)
                    raise LibsshSFTPException(
                        "Writing to remote file [%s] failed with error [%s]" % (
                            remote_file,
                            self._get_sftp_error_str(),
                        )
                    )
                buffer = f.read(SFTP_MAX_CHUNK)
            sftp.sftp_close(rf)

    def get(self, remote_file, local_file):
        cdef sftp.sftp_file rf
        cdef char *read_buffer = NULL
        cdef sftp.sftp_attributes attrs

        remote_file_b = remote_file
        if isinstance(remote_file_b, unicode):
            remote_file_b = remote_file.encode("utf-8")

        attrs = sftp.sftp_stat(self._libssh_sftp_session, remote_file_b)
        if attrs is NULL:
            raise LibsshSFTPException("Failed to stat the remote file [%s]. Error: [%s]"
                                      % (remote_file, self._get_sftp_error_str()))
        file_size = attrs.size

        rf = sftp.sftp_open(self._libssh_sftp_session, remote_file_b, O_RDONLY, sftp.S_IRWXU)
        if rf is NULL:
            raise LibsshSFTPException("Opening remote file [%s] for read failed with error [%s]" % (remote_file, self._get_sftp_error_str()))

        try:
            with open(local_file, 'wb') as f:
                buffer_size = min(SFTP_MAX_CHUNK, file_size)
                read_buffer = <char *>PyMem_Malloc(buffer_size)
                if read_buffer is NULL:
                    raise LibsshSFTPException("Memory allocation error")

                while True:
                    file_data = sftp.sftp_read(rf, <void *>read_buffer, sizeof(char) * buffer_size)
                    if file_data == 0:
                        break
                    elif file_data < 0:
                        sftp.sftp_close(rf)
                        raise LibsshSFTPException("Reading data from remote file [%s] failed with error [%s]"
                                                  % (remote_file, self._get_sftp_error_str()))

                    bytes_written = f.write(read_buffer[:file_data])
                    if bytes_written and file_data != bytes_written:
                        sftp.sftp_close(rf)
                        raise LibsshSFTPException("Number of bytes [%s] read from remote file [%s]"
                                                  " does not match number of bytes [%s] written to local file [%s]"
                                                  " due to error [%s]"
                                                  % (file_data, remote_file, bytes_written, local_file, self._get_sftp_error_str()))
        finally:
            if read_buffer is not NULL:
                PyMem_Free(read_buffer)
        sftp.sftp_close(rf)

    def close(self):
        if self._libssh_sftp_session is not NULL:
            sftp.sftp_free(self._libssh_sftp_session)
            self._libssh_sftp_session = NULL

    def _get_sftp_error_str(self):
        error = sftp.sftp_get_error(self._libssh_sftp_session)
        if error in MSG_MAP and error != sftp.SSH_FX_FAILURE:
            return MSG_MAP[error]
        return "Generic failure: %s" % self.session._get_session_error_str()
