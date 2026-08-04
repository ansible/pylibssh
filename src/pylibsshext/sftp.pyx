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

from posix.fcntl cimport O_CREAT, O_RDONLY, O_TRUNC, O_WRONLY

from cpython.mem cimport PyMem_Free, PyMem_Malloc

from pylibsshext.errors cimport LibsshSFTPException
from pylibsshext.session cimport get_libssh_session


# The maximum SFTP chunk size we attempt to transfer in a single SFTP packet.
# The value 32kB is a safe fallback when we cannot determine better value from
# the server, for example using limits@openssh.com (since libssh 0.11.0).
SFTP_MAX_CHUNK = 32_768

_NO_ATTR_ERR = "The attribute {attr_name} is not available"


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

    @property
    def version(self) -> int:
        """
        The SFTP protocol version.

        The most common protocol version is version 3 implemenbed by OpenSSH. The libssh
        implements also some parts of version 4 which is partially incompatible with the
        previous versions.
        """
        return sftp.sftp_server_version(self._libssh_sftp_session)

    def stat(self, remote_path: str | os.PathLike[str]) -> Attributes:
        """
        Requests information about remote file or directory.

        Requests information about file or directory from the remote server.
        This information includes its size, owner, group, type and many more.

        :param remote_path: The remote file or directory to find information about

        :raises LibsshSFTPException: If operation failed.

        :return: Remote file or directory attributes
        """
        cdef sftp.sftp_attributes attrs

        remote_path_b = os.fspath(remote_path)
        if isinstance(remote_path_b, str):
            remote_path_b = remote_path_b.encode("utf-8")
        else:
            raise TypeError(f"Expected str or os.PathLike, got {type(remote_path).__name__}")

        attrs = sftp.sftp_stat(self._libssh_sftp_session, remote_path_b)
        if attrs is NULL:
            raise LibsshSFTPException(
                "Failed to stat the remote file [%s]. Error: [%s]"
                % (
                    remote_path,
                    self._get_sftp_error_str(),
                ),
            )
        return Attributes._from_ptr(attrs, self.version)

    def put(self, local_file, remote_file):
        """
        Upload local file to remote server.

        :param local_file: The file name on the local file system to upload
        :type local_file: str or os.PathLike

        :param remote_file: The path to upload the file on the remote system
        :type remote_file: str or bytes
        """
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
                        self._get_sftp_error_str(),
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

    def get(self, remote_file, local_file):
        """
        Download remote file to local path.

        :param remote_file: The file path on the remote system to download
        :type remote_file: str or bytes

        :param local_file: The path on the local file system to place the downloaded file
        :type local_file: str or os.PathLike
        """
        cdef sftp.sftp_file rf
        cdef char *read_buffer = NULL

        remote_file_b = remote_file
        if isinstance(remote_file_b, unicode):
            remote_file_b = remote_file.encode("utf-8")

        attrs = self.stat(remote_file)
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


cdef class Attributes:
    """
    SFTP Attributes providing information about remote file.

    Note, that not all the information is always available (see the doc string describing availability).
    Unavailable properties raise LookupError exception.
    """

    @staticmethod
    cdef Attributes _from_ptr(sftp.sftp_attributes ptr, int version):
        """Create a new object from a raw C pointer."""
        if ptr is NULL:
            raise LibsshSFTPException("Can not construct Attributes from NULL")

        cdef Attributes obj = Attributes.__new__(Attributes)
        obj.attrs = ptr
        obj.version = version
        return obj

    def __dealloc__(self):
        if self.attrs is NULL:
            return

        sftp.sftp_attributes_free(self.attrs)
        self.attrs = NULL

    @property
    def name(self) -> str:
        """
        The file name.

        Note, that this attribute is not set when Attributes come from stat().
        """
        if self.attrs.name is NULL:
            raise LookupError(_NO_ATTR_ERR.format(attr_name='name'))
        return self.attrs.name.decode('utf-8')

    @property
    def longname(self) -> str:
        """
        The extended name (i. e. output of `ls -l`).

        Note, that this attribute is not set when Attributes come from stat().
        This is set only since SFTP protocol version 3 with OpenSSH.
        """
        if self.attrs.longname is NULL:
            raise LookupError(_NO_ATTR_ERR.format(attr_name='longname'))
        return self.attrs.longname.decode('utf-8')

    @property
    def owner(self) -> str:
        """
        The file owner.

        Note, that this attribute is not set when Attributes come from stat().
        This is set only since SFTP protocol version 4 or with OpenSSH.
        """
        if self.attrs.flags & sftp.SSH_FILEXFER_ATTR_OWNERGROUP == 0 or self.attrs.owner is NULL:
            raise LookupError(_NO_ATTR_ERR.format(attr_name='owner'))
        return self.attrs.owner.decode('utf-8')

    @property
    def group(self) -> str:
        """
        The file group.

        Note, that this attribute is not set when Attributes come from stat().
        This is set only since SFTP protocol version 4 or with OpenSSH.
        """
        if self.attrs.flags & sftp.SSH_FILEXFER_ATTR_OWNERGROUP == 0 or self.attrs.group is NULL:
            raise LookupError(_NO_ATTR_ERR.format(attr_name='group'))
        return self.attrs.group.decode('utf-8')

    @property
    def is_regular(self) -> bool:
        """
        Attribute representing whether the object is a regular file or not.
        """
        return self.attrs.type == sftp.SSH_FILEXFER_TYPE_REGULAR

    @property
    def is_dir(self) -> bool:
        """
        Attribute representing whether the object is a directory or not.
        """
        return self.attrs.type == sftp.SSH_FILEXFER_TYPE_DIRECTORY

    @property
    def is_symlink(self) -> bool:
        """
        Attribute representing whether the object is a symlink or not.
        """
        return self.attrs.type == sftp.SSH_FILEXFER_TYPE_SYMLINK

    @property
    def is_special(self) -> bool:
        """
        Attribute representing whether the object is a special file or not.
        """
        return self.attrs.type == sftp.SSH_FILEXFER_TYPE_SPECIAL

    @property
    def is_unknown(self) -> bool:
        """
        Attribute representing whether the object is an unknown file type or not.
        """
        return self.attrs.type == sftp.SSH_FILEXFER_TYPE_UNKNOWN

    @property
    def size(self) -> int:
        """
        The file size.

        This is set only with SSH_FILEXFER_ATTR_SIZE flag
        """
        if self.attrs.flags & sftp.SSH_FILEXFER_ATTR_SIZE == 0:
            raise LookupError(_NO_ATTR_ERR.format(attr_name='size'))
        return self.attrs.size

    @property
    def uid(self) -> int:
        """
        The numerical user ID of the file owner.

        This is set only with SSH_FILEXFER_ATTR_UIDGID flag
        """
        if self.attrs.flags & sftp.SSH_FILEXFER_ATTR_UIDGID == 0:
            raise LookupError(_NO_ATTR_ERR.format(attr_name='uid'))
        return self.attrs.uid

    @property
    def gid(self) -> int:
        """
        The numerical group ID of the file group.

        This is set only with SSH_FILEXFER_ATTR_UIDGID flag
        """
        if self.attrs.flags & sftp.SSH_FILEXFER_ATTR_UIDGID == 0:
            raise LookupError(_NO_ATTR_ERR.format(attr_name='gid'))
        return self.attrs.gid

    @property
    def permissions(self) -> int:
        """
        The numerical file permissions as returned by stat().

        This is set only with SSH_FILEXFER_ATTR_PERMISSIONS flag
        """
        if self.attrs.flags & sftp.SSH_FILEXFER_ATTR_PERMISSIONS == 0:
            raise LookupError(_NO_ATTR_ERR.format(attr_name='permissions'))
        return self.attrs.permissions

    @property
    def atime(self) -> int:
        """
        The file access time.

        This is set only in SFTP protocol version 3 with SSH_FILEXFER_ATTR_ACMODTIME flag
        """
        if self.attrs.flags & sftp.SSH_FILEXFER_ATTR_ACMODTIME == 0:
            raise LookupError(_NO_ATTR_ERR.format(attr_name='atime'))
        return self.attrs.atime

    @property
    def mtime(self) -> int:
        """
        The file modification time.

        This is set only in SFTP protocol version 3 with SSH_FILEXFER_ATTR_ACMODTIME flag
        """
        if self.attrs.flags & sftp.SSH_FILEXFER_ATTR_ACMODTIME == 0:
            raise LookupError(_NO_ATTR_ERR.format(attr_name='mtime'))
        return self.attrs.mtime
