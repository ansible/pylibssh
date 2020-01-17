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
from posix.fcntl cimport O_WRONLY, O_CREAT, O_TRUNC

from pylibssh.session cimport get_libssh_session
from pylibssh.errors cimport LibsshSFTPException


cdef class SFTP:
	def __cinit__(self, session):
		self.session = session
		self._libssh_sftp_session = sftp.sftp_new(get_libssh_session(session))
		if self._libssh_sftp_session is NULL:
			raise LibsshSFTPException("Failed to create new session", session)
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
				raise LibsshSFTPException(self, "Opening remote file [%s] for write failed" % remote_file)
			buffer = f.read(1024)
			while buffer != b"":
				length = len(buffer)
				written = sftp.sftp_write(rf, PyBytes_AS_STRING(buffer), length)
				if written != length:
					sftp.sftp_close(rf)
					raise LibsshSFTPException(self, "Writing to remote file [%s] failed" % remote_file)
				buffer = f.read(1024)
			sftp.sftp_close(rf)
