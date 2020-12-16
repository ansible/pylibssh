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

import os

from cpython.bytes cimport PyBytes_AS_STRING
from cpython.mem cimport PyMem_Free, PyMem_Malloc

from pylibsshext.errors cimport LibsshSCPException
from pylibsshext.session cimport get_libssh_session


cdef class SCP:
    def __cinit__(self, session):
        self.session = session
        self._libssh_session = get_libssh_session(session)

    def put(self, local_file, remote_file):
        """
        Create an SCP channel and send a file to the remote host over that channel.

        :param local_file: The path on the local host where the file will be read from
        :type local_file: str

        :param remote_file: The path on the remote host where the file should be placed
        :type remote_file: str
        """
        remote_file_b = remote_file
        if isinstance(remote_file_b, unicode):
            remote_file_b = remote_file.encode("utf-8")
        remote_dir_b, filename_b = os.path.split(remote_file_b)
        if not remote_dir_b:
            remote_dir_b = b"."

        with open(local_file, "rb") as f:
            file_stat = os.fstat(f.fileno())
            file_size = file_stat.st_size
            file_mode = file_stat.st_mode & 0o777

            # Create the SCP session in write mode
            scp = libssh.ssh_scp_new(self._libssh_session, libssh.SSH_SCP_WRITE, remote_file_b)
            if scp is NULL:
                raise LibsshSCPException(
                    "Allocating SCP session of remote file [{path!s}] for "
                    "write failed with error [{err!s}]".
                    format(path=remote_file, err=self._get_ssh_error_str()),
                )

            # Initialize the SCP channel
            rc = libssh.ssh_scp_init(scp)
            if rc != libssh.SSH_OK:
                libssh.ssh_scp_free(scp)
                raise LibsshSCPException(
                    "Initializing SCP session of remote file [{path!s}] for "
                    "write failed with error [{err!s}]".
                    format(path=remote_file, err=self._get_ssh_error_str()),
                )

            try:
                # Begin to send to the file
                rc = libssh.ssh_scp_push_file(scp, filename_b, file_size, file_mode)
                if rc != libssh.SSH_OK:
                    raise LibsshSCPException("Can't open remote file: %s" % self._get_ssh_error_str())

                # Write to the open file
                rc = libssh.ssh_scp_write(scp, PyBytes_AS_STRING(f.read()), file_size)
                if rc != libssh.SSH_OK:
                    raise LibsshSCPException("Can't write to remote file: %s" % self._get_ssh_error_str())
            finally:
                libssh.ssh_scp_close(scp)
                libssh.ssh_scp_free(scp)

            return libssh.SSH_OK

    def get(self, remote_file, local_file):
        """
        Create an SCP channel and retrieve a file from the remote host over that channel.

        :param remote_file: The path on the remote host where the file will be read from
        :type remote_file: str

        :param local_file: The path on the local host where the file should be placed
        :type local_file: str
        """
        cdef char *read_buffer

        remote_file_b = remote_file
        if isinstance(remote_file_b, unicode):
            remote_file_b = remote_file.encode("utf-8")

        # Create the SCP session in read mode
        scp = libssh.ssh_scp_new(self._libssh_session, libssh.SSH_SCP_READ, remote_file_b)
        if scp is NULL:
            raise LibsshSCPException("Allocating SCP session of remote file [%s] for write failed with error [%s]" % (remote_file, self._get_ssh_error_str()))

        # Initialize the SCP channel
        rc = libssh.ssh_scp_init(scp)
        if rc != libssh.SSH_OK:
            libssh.ssh_scp_free(scp)
            raise LibsshSCPException("Initializing SCP session of remote file [%s] for write failed with error [%s]" % (remote_file, self._get_ssh_error_str()))

        try:
            # Request to pull the file
            rc = libssh.ssh_scp_pull_request(scp)
            if rc != libssh.SSH_SCP_REQUEST_NEWFILE:
                raise LibsshSCPException("Error receiving information about file: %s" % self._get_ssh_error_str())

            size = libssh.ssh_scp_request_get_size(scp)
            mode = libssh.ssh_scp_request_get_permissions(scp)

            read_buffer = <char *>PyMem_Malloc(size)
            if read_buffer is NULL:
                raise LibsshSCPException("Memory allocation error")

            # Indicate the transfer is ready to begin
            libssh.ssh_scp_accept_request(scp)
            if rc == libssh.SSH_ERROR:
                raise LibsshSCPException("Failed to start read request: %s" % self._get_ssh_error_str())

            # Read the file
            rc = libssh.ssh_scp_read(scp, read_buffer, size)
            if rc == libssh.SSH_ERROR:
                raise LibsshSCPException("Error receiving file data: %s" % self._get_ssh_error_str())

            py_file_bytes = read_buffer[:size]
            with open(local_file, "wb") as f:
                f.write(py_file_bytes)
            if mode >= 0:
                os.chmod(local_file, mode)

            # Make sure we have finished requesting files
            rc = libssh.ssh_scp_pull_request(scp)
            if rc != libssh.SSH_SCP_REQUEST_EOF:
                raise LibsshSCPException("Unexpected request: %s" % self._get_ssh_error_str())

        finally:
            if read_buffer is not NULL:
                PyMem_Free(read_buffer)
            libssh.ssh_scp_close(scp)
            libssh.ssh_scp_free(scp)

        return libssh.SSH_OK

    def _get_ssh_error_str(self):
        return libssh.ssh_get_error(self._libssh_session)
