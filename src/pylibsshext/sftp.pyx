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

import collections as _c
import typing as _t


if _t.TYPE_CHECKING:
    import os  # pragma: no cover
    import types as _tps  # pragma: no cover

from posix.fcntl cimport O_CREAT, O_RDONLY, O_TRUNC, O_WRONLY

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

cdef class SFTP:
    def __cinit__(self, session):
        self.session = session
        self._limits = NULL
        self._libssh_sftp_session = sftp.sftp_new(get_libssh_session(session))
        if self._libssh_sftp_session is NULL:
            raise LibsshSFTPException("Failed to create new session")
        if sftp.sftp_init(self._libssh_sftp_session) != libssh.SSH_OK:
            raise LibsshSFTPException("Error initializing SFTP session")

        if sftp.HAVE_SFTP_AIO:
            # Note: sftp_limits() always returns non-NULL even if the server does not
            # support the limits@openssh.com extension, because libssh implicitly falls
            # back to safe default limits. A NULL return only indicates an internal error
            # (such as an allocation failure).
            self._limits = sftp.sftp_limits(self._libssh_sftp_session)
            if self._limits is NULL:
                sftp_error = self._get_sftp_error_str()
                raise LibsshSFTPException(
                    f"Failed to get remote SFTP limits [{sftp_error!s}]"
                )

    def __dealloc__(self):
        sftp.sftp_limits_free(self._limits)
        self._limits = NULL
        sftp.sftp_free(self._libssh_sftp_session)
        self._libssh_sftp_session = NULL

    def _cap_io_size(self, length: int, limit: int) -> int:
        """
        Calculate the number of bytes to write or read over the channel in one chunk

        Takes the remaining bytes in the file and the server enforced limit for read
        or write. The length is capped to the provided limits, but hard-limited by
        255k (SFTP_MAX_CHUNK_LIMIT).
        The care is also taken to make sure the server does not provide
        maliciously small value like 0, which would cause DoS.

        :param length: Requested maximum file transfer limit
        :param limit: The server limit through limits@openssh.com (or libssh default fallback)

        :returns: The number of bytes to read or write
        """
        if limit == 0:  # unlimited
            return SFTP_MAX_CHUNK_LIMIT
        limit = max(limit, SFTP_MAX_CHUNK)
        limit = min(limit, SFTP_MAX_CHUNK_LIMIT)
        return min(length, limit)

    def _cap_write_size(self, length: int) -> int:
        """
        Calculate the number of bytes to write over the channel in one chunk

        :param length: Requested maximum file transfer limit

        :returns: The number of bytes to write
        """
        if self._limits == NULL:
            return min(length, SFTP_MAX_CHUNK)
        return self._cap_io_size(length, self._limits.max_write_length)

    def _cap_read_size(self, length: int) -> int:
        """
        Calculate the number of bytes to read over the channel in one chunk

        :param length: Requested maximum file transfer limit

        :returns: The number of bytes to read
        """
        if self._limits == NULL:
            return min(length, SFTP_MAX_CHUNK)
        return self._cap_io_size(length, self._limits.max_read_length)

    def put(self, local_file: str | os.PathLike[str], remote_file: str) -> None:
        """
        Upload local file to remote server.

        :param local_file: The file name on the local file system to upload

        :param remote_file: The path to upload the file on the remote system

        :raises ValueError: When remote path contains invalid null bytes
        :raises LibsshSFTPException: When opening or writing to the remote file fails
        """
        cdef bint async_mode = sftp.HAVE_SFTP_AIO
        cdef size_t chunk_size = self._cap_write_size(SFTP_MAX_CHUNK_LIMIT) if async_mode else SFTP_MAX_CHUNK
        cdef bytearray write_buffer = bytearray(chunk_size)
        buffer_view = memoryview(write_buffer)
        cdef bint is_eof = False
        cdef ssize_t bytes_read

        with open(local_file, 'rb') as local_fd, _RemoteFile(
            sftp_obj=self,
            path=remote_file,
            flags=O_WRONLY | O_CREAT | O_TRUNC,
            async_mode=async_mode,
        ) as remote_fd:
            if async_mode:
                # start multiple requests before waiting for responses
                for _ in range(SFTP_MAX_REQUESTS):
                    bytes_read = local_fd.readinto(write_buffer)
                    if bytes_read == 0:
                        is_eof = True
                        break
                    remote_fd.write(buffer_view[:bytes_read])

                while remote_fd.has_pending_aio_requests():
                    remote_fd.aio_wait_write()

                    if not is_eof:
                        bytes_read = local_fd.readinto(write_buffer)
                        if bytes_read == 0:
                            is_eof = True
                        else:
                            remote_fd.write(buffer_view[:bytes_read])
            else:
                while True:
                    bytes_read = local_fd.readinto(write_buffer)
                    if bytes_read == 0:
                        break

                    remote_fd.write(buffer_view[:bytes_read])

    def get(self, remote_file: str, local_file: str | os.PathLike[str]) -> None:
        """
        Download remote file to local path.

        :param remote_file: The file path on the remote system to download

        :param local_file: The path on the local file system to place the downloaded file

        :raises LibsshSFTPException: When opening or reading the remote file fails
        :raises ValueError: When remote path contains invalid null bytes
        """
        cdef bint async_mode = sftp.HAVE_SFTP_AIO
        cdef size_t chunk_size = self._cap_read_size(SFTP_MAX_CHUNK_LIMIT) if async_mode else SFTP_MAX_CHUNK
        cdef bytearray read_buffer = bytearray(chunk_size)
        buffer_view = memoryview(read_buffer)
        cdef bint is_eof = False
        cdef ssize_t bytes_read

        with _RemoteFile(
            sftp_obj=self,
            path=remote_file,
            flags=O_RDONLY,
            async_mode=async_mode,
        ) as remote_fd, open(local_file, 'wb') as local_fd:
            if async_mode:
                # Dispatch initial probe request -- handles small files with one round trip
                remote_fd.aio_begin_read(chunk_size)

                while remote_fd.has_pending_aio_requests():
                    bytes_read = remote_fd.readinto(read_buffer)

                    # write the local file
                    if bytes_read > 0:
                        local_fd.write(buffer_view[:bytes_read])

                    if bytes_read < chunk_size:
                        is_eof = True

                    if not is_eof:
                        # There are more data to read. Do it async with up to
                        # SFTP_MAX_REQUESTS in flight requests
                        while remote_fd.pending_aio_requests() < SFTP_MAX_REQUESTS:
                            remote_fd.aio_begin_read(chunk_size)
            else:
                while True:
                    bytes_read = remote_fd.readinto(read_buffer)
                    if bytes_read == 0:
                        break

                    local_fd.write(buffer_view[:bytes_read])

    def close(self):
        sftp.sftp_limits_free(self._limits)
        self._limits = NULL
        sftp.sftp_free(self._libssh_sftp_session)
        self._libssh_sftp_session = NULL

    def _get_sftp_error_str(self):
        error = sftp.sftp_get_error(self._libssh_sftp_session)
        if error in MSG_MAP and error != sftp.SSH_FX_FAILURE:
            return MSG_MAP[error]
        return "Generic failure: %s" % self.session._get_session_error_str()


cdef class _RemoteFile:
    """
    Remote file handle facade.

    Implements a standard context manager interface for
    convenient access lifetime management.
    """
    def __cinit__(
        self,
        *,
        sftp_obj: SFTP,
        path: str,
        int flags,
        bint async_mode = False,
    ) -> None:
        """
        Initialize a remote file handle instance.

        :param sftp_obj: The SFTP session
        :param path: The path to remote file
        :param flags: The bit map of flags from ``posix.fcntl.O_*``
        :param async_mode: Whether to use asynchronous IO

        :raises ValueError: When remote path contains invalid null bytes
        :raises NotImplementedError: When asynchronous mode is requested on libssh < 0.11.0
        :raises LibsshSFTPException: When opening of remote file fails
        """
        self._fd = NULL
        if "\0" in path:
            raise ValueError(
                f"Invalid remote file path with embedded null byte: {path!r}",
            )
        if async_mode and not sftp.HAVE_SFTP_AIO:
            raise NotImplementedError(
                "Asynchronous SFTP requires libssh >= 0.11.0",
            )

        self._sftp = sftp_obj
        self._path = path
        self._async_mode = async_mode
        self._aio_queue = _c.deque() if async_mode else None
        # Keep the encoded bytes alive while the pointer is used:
        # https://cython.rtfd.io/en/latest/src/tutorial/strings.html#encoding-text-to-bytes
        b_path = path.encode("utf-8")

        self._fd = sftp.sftp_open(
            sftp_obj._libssh_sftp_session,
            b_path,
            flags,
            sftp.S_IRWXU,
        )
        if self._fd is not NULL:
            return

        file_open_mode = "writing" if flags & O_WRONLY else "reading"
        sftp_error = sftp_obj._get_sftp_error_str()
        raise LibsshSFTPException(
            f"Opening remote file [{path!s}] for {file_open_mode!s} "
            f"failed with error [{sftp_error!s}]",
        )

    def write(self, const unsigned char[:] data) -> int:
        """
        Write data directly to the remote file.

        In asynchronous mode, begins an async write request and queues it internally.
        Call :meth:`aio_wait_write` to wait for and finalize queued write operations.

        :param data: The buffer data to write to the remote file

        :returns: Number of bytes written

        :raises LibsshSFTPException: When writing failed or wrong amount of data was written
        """
        cdef ssize_t length = data.shape[0]
        if length == 0:
            return 0

        cdef const char* c_buf = <const char*>&data[0]
        cdef ssize_t written
        cdef sftp.sftp_aio raw_aio = NULL

        if self._async_mode:
            written = sftp.sftp_aio_begin_write(self._fd, c_buf, length, &raw_aio)
            if written == length:
                c_aio = _C_AIO.from_ptr(raw_aio)
                self._aio_queue.append(c_aio)
                return written
        else:
            written = sftp.sftp_write(self._fd, c_buf, length)
            if written == length:
                return written

        sftp_error = self._sftp._get_sftp_error_str()
        raise LibsshSFTPException(
            f"Writing to remote file [{self._path!s}] failed with error [{sftp_error!s}]"
        )

    def aio_wait_write(self) -> int:
        """
        Wait for the next asynchronous write request to complete.

        :returns: Number of bytes written

        :raises LibsshSFTPException: When write request failed
        :raises NotImplementedError: When asynchronous mode is requested on libssh < 0.11.0
        """
        if not self._async_mode:
            raise NotImplementedError(
                "Asynchronous SFTP requires libssh >= 0.11.0",
            )

        cdef _C_AIO aio = self._aio_queue.popleft()
        cdef ssize_t written = sftp.sftp_aio_wait_write(&aio.aio)
        aio.aio = NULL
        if written != libssh.SSH_ERROR:
            return written

        sftp_error = self._sftp._get_sftp_error_str()
        raise LibsshSFTPException(
            f"Writing to remote file [{self._path!s}] failed with error [{sftp_error!s}]"
        )

    def aio_begin_read(self, size_t length) -> None:
        """
        Begin an asynchronous read request and queue it internally.

        :param length: Number of bytes to request

        :raises LibsshSFTPException: When read request failed
        :raises NotImplementedError: When asynchronous mode is requested on libssh < 0.11.0
        """
        if not self._async_mode:
            raise NotImplementedError(
                "Asynchronous SFTP requires libssh >= 0.11.0",
            )

        cdef sftp.sftp_aio raw_aio = NULL
        cdef ssize_t requested = sftp.sftp_aio_begin_read(self._fd, length, &raw_aio)
        if requested == length:
            c_aio = _C_AIO.from_ptr(raw_aio)
            self._aio_queue.append(c_aio)
            return

        sftp_error = self._sftp._get_sftp_error_str()
        raise LibsshSFTPException(
            f"Reading data from remote file [{self._path!s}] failed with error [{sftp_error!s}]"
        )

    def readinto(self, data: bytearray) -> int:
        """
        Read data from the remote file descriptor into provided bytearray.

        In asynchronous mode, waits for the next queued async read request
        initialized by :meth:`aio_begin_read`.

        :param data: The buffer where the read data will be placed

        :returns: Number of bytes read

        :raises LibsshSFTPException: When reading failed
        """
        cdef char* c_buf = data
        cdef ssize_t length = len(data)
        cdef ssize_t file_data
        cdef _C_AIO aio

        if self._async_mode:
            aio = self._aio_queue.popleft()
            file_data = sftp.sftp_aio_wait_read(&aio.aio, c_buf, length)
            aio.aio = NULL
        else:
            file_data = sftp.sftp_read(self._fd, c_buf, length)

        if file_data >= 0:
            return file_data

        sftp_error = self._sftp._get_sftp_error_str()
        raise LibsshSFTPException(
            f"Reading data from remote file [{self._path!s}] failed with error [{sftp_error!s}]"
        )

    def pending_aio_requests(self) -> int:
        """
        Return the number of in-flight asynchronous requests in the queue.

        :returns: Number of pending requests
        """
        return len(self._aio_queue) if self._aio_queue is not None else 0

    def has_pending_aio_requests(self) -> bool:
        """
        Check whether there are pending asynchronous requests in the queue.

        :returns: True if requests are pending, False otherwise
        """
        return self.pending_aio_requests() > 0

    cdef void _close(self) noexcept:
        if self._fd is NULL:
            return

        if self._aio_queue is not None:
            self._aio_queue.clear()

        sftp.sftp_close(self._fd)
        self._fd = NULL

    def __dealloc__(self) -> None:
        self._close()

    def __enter__(self) -> _t.Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: _tps.TracebackType | None,
    ) -> None:
        self._close()


cdef class _C_AIO:
    def __cinit__(self):
        self.aio = NULL

    @staticmethod
    cdef _C_AIO from_ptr(sftp.sftp_aio aio):
        cdef _C_AIO obj = _C_AIO.__new__(_C_AIO)
        obj.aio = aio
        return obj

    def __dealloc__(self):
        sftp.sftp_aio_free(self.aio)
        self.aio = NULL
