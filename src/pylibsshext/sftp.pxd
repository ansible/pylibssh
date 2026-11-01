# distutils: libraries = ssh
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
#
from pylibsshext.includes cimport libssh, sftp
from pylibsshext.session cimport Session


cdef class SFTP:
    cdef Session session
    cdef sftp.sftp_session _libssh_sftp_session
    cdef sftp.sftp_limits_t _limits
    cdef object _transfer

cdef class _BaseRemoteFile:
    cdef sftp.sftp_file _fd
    cdef SFTP _sftp
    cdef str _path
    cdef void _close(self) noexcept

cdef class _RemoteFile(_BaseRemoteFile):
    pass

cdef class _PipelinedRemoteFile(_BaseRemoteFile):
    cdef object _aio_queue
    cdef void _close(self) noexcept

cdef class _C_AIO:
    cdef sftp.sftp_aio aio

    @staticmethod
    cdef _C_AIO from_ptr(sftp.sftp_aio aio)

cdef class _BaseTransfer:
    cdef SFTP _sftp

cdef class _SyncTransfer(_BaseTransfer):
    pass

cdef class _PipelinedTransfer(_BaseTransfer):
    pass
