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
            self._open_remote_file_cm = _PipelinedRemoteFile
        else:
            self._open_remote_file_cm = _RemoteFile

    def __dealloc__(self):
        sftp.sftp_limits_free(self._limits)
        self._limits = NULL
        sftp.sftp_free(self._libssh_sftp_session)
        self._libssh_sftp_session = NULL

    def _cap_io_size(self, limit: int) -> int:
        """
        Calculate the safe chunk size for reading or writing over the channel.

        Caps the server-enforced limit between a safe minimum
        (``SFTP_MAX_CHUNK``, 32 KiB) and maximum (``SFTP_MAX_CHUNK_LIMIT``, 255 KiB).
        If the server reports 0 (unlimited), ``SFTP_MAX_CHUNK_LIMIT`` is returned.
        Enforcing the floor prevents DoS from servers advertising maliciously small limits.

        :param limit: Server limit from ``limits@openssh.com`` (or libssh fallback, 0 for unlimited)

        :returns: Safe chunk size in bytes to read or write
        """
        if limit == 0:  # unlimited
            return SFTP_MAX_CHUNK_LIMIT
        return min(max(limit, SFTP_MAX_CHUNK), SFTP_MAX_CHUNK_LIMIT)

    @property
    def _cap_write_size(self) -> int:
        """
        Calculate the safe chunk size to write over the channel in one request.

        :returns: Safe chunk size in bytes to write
        """
        if self._limits == NULL:
            return SFTP_MAX_CHUNK
        return self._cap_io_size(self._limits.max_write_length)

    @property
    def _cap_read_size(self) -> int:
        """
        Calculate the safe chunk size to read over the channel in one request.

        :returns: Safe chunk size in bytes to read
        """
        if self._limits == NULL:
            return SFTP_MAX_CHUNK
        return self._cap_io_size(self._limits.max_read_length)

    def put(self, local_file: str | os.PathLike[str], remote_file: str) -> None:
        """
        Upload local file to remote server.

        :param local_file: The file name on the local file system to upload

        :param remote_file: The path to upload the file on the remote system

        :raises ValueError: When remote path contains invalid null bytes
        :raises LibsshSFTPException: When opening or writing to the remote file fails
        """
        cdef size_t chunk_size = self._cap_write_size
        cdef bytearray write_buffer = bytearray(chunk_size)
        buffer_view = memoryview(write_buffer)
        cdef ssize_t bytes_read

        with open(local_file, 'rb') as local_fd, self._open_remote_file_cm(
            sftp_obj=self,
            path=remote_file,
            flags=O_WRONLY | O_CREAT | O_TRUNC,
        ) as remote_fd:
            while True:
                bytes_read = local_fd.readinto(write_buffer)
                is_eof = bytes_read == 0
                if is_eof:
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
        cdef size_t chunk_size = self._cap_read_size
        cdef bytearray read_buffer = bytearray(chunk_size)
        buffer_view = memoryview(read_buffer)
        cdef ssize_t bytes_read

        with self._open_remote_file_cm(
            sftp_obj=self,
            path=remote_file,
            flags=O_RDONLY,
        ) as remote_fd, open(local_file, 'wb') as local_fd:
            while True:
                bytes_read = remote_fd.readinto(read_buffer)
                is_eof = bytes_read == 0
                if is_eof:
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
    Synchronous remote file handle facade.

    Implements a standard context manager interface for
    convenient access lifetime management.
    """
    def __cinit__(self, *, sftp_obj: SFTP, path: str, int flags) -> None:
        """Initialize a C-level file descriptor."""
        self._fd = NULL

    def __init__(
        self,
        *,
        SFTP sftp_obj,
        str path,
        int flags,
    ) -> None:
        """
        Initialize a remote file handle instance.

        :param sftp_obj: The SFTP session
        :param path: The path to remote file
        :param flags: The bit map of flags from ``posix.fcntl.O_*``

        :raises ValueError: When remote path contains invalid null bytes
        :raises LibsshSFTPException: When opening of remote file fails
        """
        if "\0" in path:
            raise ValueError(
                f"Invalid remote file path with embedded null byte: {path!r}",
            )

        self._sftp = sftp_obj
        self._path = path
        self._is_writer = bool(flags & O_WRONLY)
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

        :param data: The buffer data to write to the remote file

        :returns: Number of bytes written

        :raises LibsshSFTPException: When writing failed or wrong amount of data was written
        """
        cdef ssize_t length = data.shape[0]
        if length == 0:
            return 0

        cdef const char* c_buf = <const char*>&data[0]
        cdef ssize_t written = sftp.sftp_write(self._fd, c_buf, length)
        if written == length:
            return written

        sftp_error = self._sftp._get_sftp_error_str()
        raise LibsshSFTPException(
            f"Writing to remote file [{self._path!s}] failed with error [{sftp_error!s}]"
        )

    def readinto(self, data: bytearray) -> int:
        """
        Read data from the remote file descriptor into provided bytearray.

        :param data: The buffer where the read data will be placed

        :returns: Number of bytes read

        :raises LibsshSFTPException: When reading failed
        """
        cdef char* c_buf = data
        cdef ssize_t length = len(data)

        cdef ssize_t file_data = sftp.sftp_read(self._fd, c_buf, length)
        if file_data >= 0:
            return file_data

        sftp_error = self._sftp._get_sftp_error_str()
        raise LibsshSFTPException(
            f"Reading data from remote file [{self._path!s}] failed with error [{sftp_error!s}]"
        )

    cdef void _close(self) noexcept:
        if self._fd is NULL:
            return

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


cdef class _PipelinedRemoteFile(_RemoteFile):
    """
    Pipelined remote file handle facade using libssh SFTP AIO.

    Keeps up to ``SFTP_MAX_REQUESTS`` requests in flight: reads are
    issued ahead of the consumer and writes are confirmed behind the
    producer, so the same read/write loops as with :class:`_RemoteFile`
    no longer wait a full round trip per chunk.
    """

    def __init__(
        self,
        *,
        sftp_obj: SFTP,
        path: str,
        int flags,
    ) -> None:
        """
        Initialize a pipelined remote file handle instance.

        :param sftp_obj: The SFTP session
        :param path: The path to remote file
        :param flags: The bit map of flags from ``posix.fcntl.O_*``

        :raises NotImplementedError: When pipelined SFTP is requested on libssh < 0.11.0
        """
        if not sftp.HAVE_SFTP_AIO:
            raise NotImplementedError(
                "Asynchronous SFTP requires libssh >= 0.11.0",
            )
        super().__init__(sftp_obj=sftp_obj, path=path, flags=flags)
        self._aio_queue = _c.deque()
        self._drain_buffer = bytearray()

    def write(self, const unsigned char[:] data) -> int:
        """
        Queue data for writing to the remote file.

        Earlier writes are only confirmed once the queue is full, so their
        errors surface from a later call, from :meth:`flush`, or on exiting
        the context manager.

        :param data: The buffer data to write to the remote file

        :returns: Number of bytes queued

        :raises LibsshSFTPException: When writing failed
        """
        cdef size_t length = data.shape[0]
        cdef size_t queued = 0
        cdef _C_AIO aio

        if self._aio_queue and (<_C_AIO>self._aio_queue[0]).is_read:
            self._restart_reads()

        while queued < length:
            if len(self._aio_queue) >= SFTP_MAX_REQUESTS:
                self._wait_oldest_write()

            aio = self._begin_write(data[queued:])
            self._aio_queue.append(aio)
            queued += aio.length

        return length

    def flush(self) -> None:
        """
        Wait until the server confirms all the queued writes.

        :raises LibsshSFTPException: When writing failed
        """
        while self._aio_queue and not (<_C_AIO>self._aio_queue[0]).is_read:
            self._wait_oldest_write()

    def readinto(self, data: bytearray) -> int:
        """
        Read data from the remote file into provided bytearray.

        Requests for the following chunks are issued ahead, sized after
        the provided buffer.

        :param data: The buffer where the read data will be placed

        :returns: Number of bytes read

        :raises LibsshSFTPException: When reading failed
        """
        cdef char* c_buf = data
        cdef size_t length = len(data)
        cdef _C_AIO aio
        cdef ssize_t bytes_read

        if length == 0:
            return 0

        self.flush()
        if self._aio_queue and (<_C_AIO>self._aio_queue[0]).length > length:
            self._restart_reads()
        if not self._aio_queue:
            self._read_offset = sftp.sftp_tell64(self._fd)
        if len(self._drain_buffer) < length:
            # NOTE: Allocated here, where errors propagate, so that
            # NOTE: discarding the requests on close allocates nothing.
            self._drain_buffer = bytearray(length)

        while len(self._aio_queue) < SFTP_MAX_REQUESTS:
            self._aio_queue.append(self._begin_read(length))

        aio = self._aio_queue.popleft()
        bytes_read = aio.wait_read(c_buf, length)
        if bytes_read < 0:
            sftp_error = self._sftp._get_sftp_error_str()
            raise LibsshSFTPException(
                f"Reading data from remote file [{self._path!s}] "
                f"failed with error [{sftp_error!s}]"
            )

        self._read_offset += bytes_read
        # NOTE: Requests issued past a short read, including EOF,
        # NOTE: point at the wrong offsets, so they are re-issued.
        if <size_t>bytes_read < aio.length:
            self._restart_reads()

        return bytes_read

    cdef _C_AIO _begin_read(self, size_t length):
        cdef sftp.sftp_aio raw_aio = NULL
        # NOTE: libssh caps the requested length to the server limit.
        cdef ssize_t requested = sftp.sftp_aio_begin_read(
            self._fd, length, &raw_aio,
        )
        if requested > 0:
            return _C_AIO.from_ptr(raw_aio, requested, True)

        sftp_error = self._sftp._get_sftp_error_str()
        raise LibsshSFTPException(
            f"Reading data from remote file [{self._path!s}] "
            f"failed with error [{sftp_error!s}]"
        )

    cdef _C_AIO _begin_write(self, const unsigned char[:] data):
        cdef sftp.sftp_aio raw_aio = NULL
        # NOTE: libssh caps the written length to the server limit.
        cdef ssize_t written = sftp.sftp_aio_begin_write(
            self._fd, <const char*>&data[0], data.shape[0], &raw_aio,
        )
        if written > 0:
            return _C_AIO.from_ptr(raw_aio, written, False)

        sftp_error = self._sftp._get_sftp_error_str()
        raise LibsshSFTPException(
            f"Writing to remote file [{self._path!s}] failed with error [{sftp_error!s}]"
        )

    cdef void _wait_oldest_write(self) except *:
        cdef _C_AIO aio = self._aio_queue.popleft()
        if aio.wait_write() != libssh.SSH_ERROR:
            return

        sftp_error = self._sftp._get_sftp_error_str()
        raise LibsshSFTPException(
            f"Writing to remote file [{self._path!s}] failed with error [{sftp_error!s}]"
        )

    cdef void _restart_reads(self) except *:
        self._discard_in_flight()
        if sftp.sftp_seek64(self._fd, self._read_offset) == libssh.SSH_OK:
            return

        sftp_error = self._sftp._get_sftp_error_str()
        raise LibsshSFTPException(
            f"Seeking in remote file [{self._path!s}] failed with error [{sftp_error!s}]"
        )

    cdef void _discard_in_flight(self) noexcept:
        # NOTE: libssh keeps every reply until it is waited for, so
        # NOTE: dropping the requests without waiting leaks memory.
        cdef _C_AIO aio

        while self._aio_queue:
            aio = self._aio_queue.popleft()
            if aio.is_read:
                aio.wait_read(<char*>self._drain_buffer, aio.length)
            else:
                aio.wait_write()

    cdef void _close(self) noexcept:
        if self._fd is NULL:
            return

        self._discard_in_flight()
        sftp.sftp_close(self._fd)
        self._fd = NULL

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: _tps.TracebackType | None,
    ) -> None:
        try:
            if exc_type is None and self._is_writer:
                self.flush()
        finally:
            self._close()


cdef class _C_AIO:
    def __cinit__(self):
        self.aio = NULL

    @staticmethod
    cdef _C_AIO from_ptr(sftp.sftp_aio aio, size_t length, bint is_read):
        cdef _C_AIO obj = _C_AIO.__new__(_C_AIO)
        obj.aio = aio
        obj.length = length
        obj.is_read = is_read
        return obj

    cdef ssize_t wait_read(self, void* buf, size_t buf_size) noexcept:
        return sftp.sftp_aio_wait_read(&self.aio, buf, buf_size)

    cdef ssize_t wait_write(self) noexcept:
        return sftp.sftp_aio_wait_write(&self.aio)

    def __dealloc__(self):
        sftp.sftp_aio_free(self.aio)
        self.aio = NULL
