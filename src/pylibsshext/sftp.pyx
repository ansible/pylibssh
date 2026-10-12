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

import typing as _t  # noqa: WPS111


if _t.TYPE_CHECKING:  # pragma: no cover
    from types import TracebackType

from pylibsshext.errors cimport LibsshSFTPException
from pylibsshext.session cimport get_libssh_session


# The maximum SFTP chunk size we attempt to transfer in a single SFTP packet.
# The value 32kB is a safe fallback when we cannot determine better value from
# the server, for example using limits@openssh.com (since libssh 0.11.0).
SFTP_MAX_CHUNK = 32_768


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
        """
        Upload local file to remote server.

        :param local_file: The file name on the local file system to upload
        :type local_file: str or os.PathLike

        :param remote_file: The path to upload the file on the remote system
        :type remote_file: str or bytes
        """
        cdef bytearray write_buffer = bytearray(SFTP_MAX_CHUNK)

        with open(local_file, "rb") as local_fd, _RemoteFile(
            sftp_obj=self,
            path=remote_file,
            flags=O_WRONLY | O_CREAT | O_TRUNC,
        ) as remote_fd:
            while True:
                bytes_read = local_fd.readinto(write_buffer)
                is_eof = bytes_read == 0
                if is_eof:
                    break

                remote_fd.write(write_buffer, bytes_read)

    def get(self, remote_file, local_file):
        """
        Download remote file to local path.

        :param remote_file: The file path on the remote system to download
        :type remote_file: str or bytes

        :param local_file: The path on the local file system to place the downloaded file
        :type local_file: str or os.PathLike
        """
        cdef sftp.sftp_attributes attrs

        remote_file_b = remote_file
        if isinstance(remote_file_b, unicode):
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
        buffer_size = min(SFTP_MAX_CHUNK, file_size)
        cdef bytearray read_buffer = bytearray(buffer_size)
        buffer_view = memoryview(read_buffer)

        with _RemoteFile(
            sftp_obj=self,
            path=remote_file,
            flags=O_RDONLY,
        ) as remote_fd, open(local_file, 'wb') as local_fd:
            while True:
                file_data = remote_fd.read(read_buffer)
                is_eof = file_data == 0
                if is_eof:
                    break

                bytes_written = local_fd.write(buffer_view[:file_data])
                if bytes_written and file_data != bytes_written:
                    raise LibsshSFTPException(
                        f"Number of bytes [{file_data}] read from remote file "
                        f"[{remote_file!s}] does not match number of bytes "
                        f"[{bytes_written}] written to local file [{local_file!s}]"
                    )

    def close(self):
        if self._libssh_sftp_session is not NULL:
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
    def __cinit__(self, *, sftp_obj: SFTP, path: str | bytes, int flags) -> None:
        self._sftp = sftp_obj
        self._path = path
        b_path = path
        if isinstance(b_path, str):
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

    def write(self, data: bytearray, length: int) -> int:
        """
        Writes a bytearray directly to the remote file.

        :raises LibsshSessionException: When writing failed or wrong amount of data was written.
        """
        cdef const char* c_buf = data
        written = sftp.sftp_write(self._fd, c_buf, length)
        if written == length:
            return written

        sftp_error = self._sftp._get_sftp_error_str()
        raise LibsshSFTPException(
            f"Writing to remote file [{self._path!s}] failed with error [{sftp_error}]"
        )

    def read(self, data: bytearray) -> int:
        """
        Reads data from the remote file descriptor into provided bytearray.

        :raises LibsshSessionException: When reading failed.
        """
        cdef char* c_buf = data
        cdef size_t length = len(data)

        file_data = sftp.sftp_read(self._fd, c_buf, length)
        if file_data >= 0:
            return file_data

        sftp_error = self._sftp._get_sftp_error_str()
        raise LibsshSFTPException(
            f"Reading data from remote file [{self._path!s}] failed with error [{sftp_error!s}]"
        )

    def __dealloc__(self) -> None:
        if self._fd is NULL:
            return

        sftp.sftp_close(self._fd)
        self._fd = NULL

    def __enter__(self) -> _t.Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        if self._fd is NULL:
            return False

        sftp.sftp_close(self._fd)
        self._fd = NULL
