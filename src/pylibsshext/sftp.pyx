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

import os
from collections import deque
from typing import BinaryIO

from posix.fcntl cimport O_CREAT, O_RDONLY, O_TRUNC, O_WRONLY

from cpython.mem cimport PyMem_Free, PyMem_Malloc

from pylibsshext.errors cimport LibsshSFTPException
from pylibsshext.session cimport get_libssh_session


# The maximum SFTP chunk size we attempt to transfer in a single SFTP packet.
# The value 32kB is a safe fallback when we cannot determine better value from
# the server, for example using limits@openssh.com (since libssh 0.11.0).
SFTP_MAX_CHUNK = 32_768

# 255kB is absolute maximum we want to send over the SSH channel. Sending
# more will likely not work and capping at some value will prevent DoS.
SFTP_MAX_CHUNK_LIMIT = 261_120

# Default number of requests for asynchronous/overlapping uploads and downloads.
SFTP_MAX_REQUESTS = 10


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

cdef class _RemoteFile:
    """Helper class managing lifetime of remote file handle."""
    def __cinit__(self, sftp_obj: SFTP, path: str | bytes, int flags):
        mode = "write" if flags & O_WRONLY else "read"
        path_b = path
        if isinstance(path_b, str):
            path_b = path.encode("utf-8")

        self._fd = sftp.sftp_open(
            sftp_obj._libssh_sftp_session,
            path_b,
            flags,
            sftp.S_IRWXU)
        if self._fd is NULL:
            raise LibsshSFTPException(
                "Opening remote file [%s] for %s failed with error [%s]"
                % (str(path), mode, sftp_obj._get_sftp_error_str()))

    def __dealloc__(self):
        if self._fd is not NULL:
            sftp.sftp_close(self._fd)
            self._fd = NULL

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._fd is not NULL:
            sftp.sftp_close(self._fd)
            self._fd = NULL
        return False


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

    def put(self, local_file: str | os.PathLike, remote_file: str | bytes):
        """
        Upload local file to remote server.

        :param local_file: The file name on the local file system to upload

        :param remote_file: The path to upload the file on the remote system
        """
        if sftp.HAVE_SFTP_AIO:
            return SFTP_AIO(self).put(local_file, remote_file)

        # Synchronous code compatible with libssh < 0.11.0
        cdef sftp.sftp_file rf
        cdef const char* c_buf
        with open(local_file, "rb") as f:
            remote_file_b = remote_file
            if isinstance(remote_file_b, unicode):
                remote_file_b = remote_file.encode("utf-8")

            rf = sftp.sftp_open(
                self._libssh_sftp_session,
                remote_file_b,
                O_WRONLY | O_CREAT | O_TRUNC,
                sftp.S_IRWXU,
            )
            if rf is NULL:
                raise LibsshSFTPException(
                    "Opening remote file [%s] for write failed with error [%s]"
                    % (
                        remote_file,
                        self._get_sftp_error_str()
                    ),
                )
            read_buffer = f.read(SFTP_MAX_CHUNK)

            while read_buffer != b"":
                c_buf = read_buffer
                length = len(read_buffer)
                written = sftp.sftp_write(rf, c_buf, length)
                if written != length:
                    sftp.sftp_close(rf)
                    raise LibsshSFTPException(
                        "Writing to remote file [%s] failed with error [%s]"
                        % (
                            remote_file,
                            self._get_sftp_error_str(),
                        )
                    )
                read_buffer = f.read(SFTP_MAX_CHUNK)
            sftp.sftp_close(rf)

    def get(self, remote_file: str | bytes, local_file: str | os.PathLike):
        """
        Download remote file to local path.

        :param remote_file: The file path on the remote system to download
        :type remote_file: str or bytes

        :param local_file: The path on the local file system to place the downloaded file
        :type local_file: str or os.PathLike
        """
        if sftp.HAVE_SFTP_AIO:
            return SFTP_AIO(self).get(remote_file, local_file)

        # Synchronous code compatible with libssh < 0.11.0
        cdef char *read_buffer = NULL
        cdef sftp.sftp_attributes attrs

        remote_file_b = remote_file
        if isinstance(remote_file_b, str):
            remote_file_b = remote_file.encode("utf-8")

        attrs = sftp.sftp_stat(self._libssh_sftp_session, remote_file_b)
        if attrs is NULL:
            raise LibsshSFTPException(
                "Failed to stat the remote file [%s]. Error: [%s]"
                % (
                    remote_file,
                    self._get_sftp_error_str(),
                ),
            )
        file_size = attrs.size

        rf = sftp.sftp_open(self._libssh_sftp_session, remote_file_b, O_RDONLY, sftp.S_IRWXU)
        if rf is NULL:
            raise LibsshSFTPException(
                "Opening remote file [%s] for read failed with error [%s]"
                % (
                    remote_file,
                    self._get_sftp_error_str(),
                ),
            )

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
                        raise LibsshSFTPException(
                            "Reading data from remote file [%s] failed with error [%s]"
                            % (
                                remote_file,
                                self._get_sftp_error_str(),
                            ),
                        )

                    bytes_written = f.write(read_buffer[:file_data])
                    if bytes_written and file_data != bytes_written:
                        sftp.sftp_close(rf)
                        raise LibsshSFTPException(
                            "Number of bytes [%s] read from remote file [%s]"
                            " does not match number of bytes [%s] written to"
                            " local file [%s] due to error [%s]"
                            % (
                                file_data,
                                remote_file,
                                bytes_written,
                                local_file,
                                self._get_sftp_error_str(),
                            ),
                        )
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


cdef class SFTP_AIO:
    def __cinit__(self, SFTP sftp_obj):
        self._limits = NULL
        self._sftp_obj = sftp_obj
        self._sftp = sftp_obj._libssh_sftp_session

        self._limits = sftp.sftp_limits(self._sftp)
        if self._limits is NULL:
            raise LibsshSFTPException(
                "Failed to get remote SFTP limits [%s]"
                % (
                    self._sftp_obj._get_sftp_error_str(),
                ),
            )

    def __init__(self, SFTP sftp_obj):
        self._aio_queue = deque()

    def __dealloc__(self):
        if self._limits is not NULL:
            sftp.sftp_limits_free(self._limits)
            self._limits = NULL

    def _get_file_size(self, local_fd: BinaryIO) -> int:
        local_fd.seek(0, os.SEEK_END)
        file_size = local_fd.tell()
        local_fd.seek(0, os.SEEK_SET)
        return file_size

    def put(self, local_file: str | os.PathLike, remote_file: str | bytes):
        """
        Upload a local file to remote server using asynchronous IO (AIO)

        This method sends more write packets before waiting for write
        confirmation from the server. In combination with larger chunks,
        this allows faster transfers especially over large latency channels.

        :param local_file: The file name on the local file system to upload

        :param remote_file: The path to upload the file on the remote system
        """
        self._aio_queue = deque()
        self._total_bytes_requested = 0

        cdef C_AIO aio
        cdef _RemoteFile remote
        self._remote_file = remote_file
        self._local_file = local_file

        with _RemoteFile(self._sftp_obj, remote_file, O_WRONLY | O_CREAT | O_TRUNC) as remote:
            with open(local_file, "rb") as local_fd:
                self._file_size = self._get_file_size(local_fd)

                # start multiple requests before waiting for responses
                i = 0
                while i < SFTP_MAX_REQUESTS and self._total_bytes_requested < self._file_size:
                    self._put_chunk(local_fd, remote)
                    i += 1

                while len(self._aio_queue):
                    aio = self._aio_queue.popleft()
                    bytes_written = sftp.sftp_aio_wait_write(&aio.aio)
                    if bytes_written == libssh.SSH_ERROR:
                        raise LibsshSFTPException(
                            "Failed to write to remote file [%s]: error [%s]"
                            % (
                                remote_file,
                                self._sftp_obj._get_sftp_error_str(),
                            ),
                        )
                    # was freed in the wait if it did not fail
                    aio.aio = NULL

                    # whole file written
                    if self._total_bytes_requested == self._file_size:
                        continue

                    # else issue more write requests
                    self._put_chunk(local_fd, remote)

    def _cap_write_size(self, length: int) -> int:
        """
        Calculate the number of bytes to write over the channel in one chunk

        Takes the remaining bytes in the file. The output value is capped
        to the server limits but hard-limited by 255k (SFTP_MAX_CHUNK_LIMIT).
        The care is also taken to make sure the server does not provide
        maliciously small value like 0, which would cause DoS.
        """
        limit = max(self._limits.max_write_length, SFTP_MAX_CHUNK)
        limit = min(limit, SFTP_MAX_CHUNK_LIMIT)
        return min(length, limit)

    def _cap_read_size(self, length: int) -> int:
        """
        Calculate the number of bytes to read over the channel in one chunk

        Takes the remaining bytes in the file. The output value is capped
        to the server limits but hard-limited by 255k (SFTP_MAX_CHUNK_LIMIT).
        The care is also taken to make sure the server does not provide
        maliciously small value like 0, which would cause DoS.
        """
        limit = max(self._limits.max_read_length, SFTP_MAX_CHUNK)
        limit = min(limit, SFTP_MAX_CHUNK_LIMIT)
        return min(length, limit)

    def _put_chunk(self, local_fd: BinaryIO, remote: _RemoteFile):
        to_write = self._cap_write_size(self._file_size - self._total_bytes_requested)
        read_buffer = local_fd.read(to_write)
        if len(read_buffer) != to_write:
            raise LibsshSFTPException(
                "Read only [%d] but requested [%d] when reading from local file [%s]"
                % (
                    len(read_buffer),
                    to_write,
                    self._local_file,
                ),
            )

        cdef sftp.sftp_aio aio = NULL
        cdef const char* c_buf = read_buffer
        bytes_requested = sftp.sftp_aio_begin_write(remote._fd, c_buf, to_write, &aio)
        if bytes_requested != to_write:
            raise LibsshSFTPException(
                "Failed to write chunk of size [%d] of file [%s] with error [%s]"
                % (
                    to_write,
                    self._remote_file,
                    self._sftp_obj._get_sftp_error_str(),
                ),
            )
        self._total_bytes_requested += bytes_requested
        c_aio = C_AIO()
        c_aio.aio = aio
        self._aio_queue.append(c_aio)

    def get(self, remote_file: str | bytes, local_file: str or os.PathLike):
        """
        Download a remote file to local path using asynchronous IO (AIO)

        This method sends more read request packets before waiting for response
        data from the server. In combination with larger chunks, this allows
        faster transfers especially over large latency channels.
        """
        self._aio_queue = deque()
        self._total_bytes_requested = 0

        cdef C_AIO aio
        cdef _RemoteFile remote
        cdef sftp.sftp_attributes attrs
        cdef char *read_buffer = NULL
        self._remote_file = remote_file

        remote_file_b = remote_file
        if isinstance(remote_file_b, str):
            remote_file_b = remote_file.encode("utf-8")

        attrs = sftp.sftp_stat(self._sftp, remote_file_b)
        if attrs is NULL:
            raise LibsshSFTPException(
                "Failed to stat the remote file [%s] with error [%s]"
                % (
                    remote_file,
                    self._sftp_obj._get_sftp_error_str(),
                ),
            )
        self._file_size = attrs.size
        sftp.sftp_attributes_free(attrs)

        buffer_size = self._cap_read_size(self._file_size)
        try:
            read_buffer = <char *>PyMem_Malloc(buffer_size)
            if buffer_size and read_buffer is NULL:
                raise LibsshSFTPException("Memory allocation error")

            with _RemoteFile(self._sftp_obj, remote_file, O_RDONLY) as remote:
                with open(local_file, 'wb') as lccal_fd:
                    # start multiple read requests before waiting for responses
                    i = 0
                    while i < SFTP_MAX_REQUESTS and self._total_bytes_requested < self._file_size:
                        self._get_chunk(remote)
                        i += 1

                    while len(self._aio_queue):
                        aio = self._aio_queue.popleft()
                        bytes_read = sftp.sftp_aio_wait_read(&aio.aio, <void *>read_buffer, buffer_size)
                        if bytes_read == libssh.SSH_ERROR:
                            raise LibsshSFTPException(
                                "Failed to read from remote file [%s]: error [%s]"
                                % (
                                    remote_file,
                                    self._sftp_obj._get_sftp_error_str(),
                                ),
                            )
                        # was freed in the wait if it did not fail -- otherwise the __dealloc__ will free it
                        aio.aio = NULL

                        # write the local file
                        bytes_written = lccal_fd.write(read_buffer[:bytes_read])
                        if bytes_written != bytes_read:
                            raise LibsshSFTPException(
                                "Number of bytes [%d] read from remote file [%s]"
                                " does not match number of bytes [%d] written to"
                                " local file [%s]"
                                % (
                                    bytes_read,
                                    remote_file,
                                    bytes_written,
                                    local_file,
                                ),
                            )

                        # whole file read
                        if self._total_bytes_requested == self._file_size:
                            continue

                        # else issue more read requests
                        self._get_chunk(remote)

        finally:
            if read_buffer is not NULL:
                PyMem_Free(read_buffer)

    def _get_chunk(self, remote: _RemoteFile):
        to_read = self._cap_read_size(self._file_size - self._total_bytes_requested)
        cdef sftp.sftp_aio aio = NULL
        bytes_requested = sftp.sftp_aio_begin_read(remote._fd, to_read, &aio)
        if bytes_requested != to_read:
            raise LibsshSFTPException(
                "Failed to request to read chunk of size [%d] of file [%s] with error [%s]"
                % (
                    to_read,
                    self._remote_file,
                    self._sftp_obj._get_sftp_error_str(),
                ),
            )
        self._total_bytes_requested += bytes_requested
        c_aio = C_AIO()
        c_aio.aio = aio
        self._aio_queue.append(c_aio)


cdef class C_AIO:
    def __cinit__(self):
        self.aio = NULL

    def __dealloc__(self):
        sftp.sftp_aio_free(self.aio)
        self.aio = NULL
