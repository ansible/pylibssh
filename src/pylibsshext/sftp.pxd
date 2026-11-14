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
from libc cimport stdint

from pylibsshext.includes cimport libssh, sftp
from pylibsshext.session cimport Session


cdef class SFTP:
    cdef Session session
    cdef sftp.sftp_session _libssh_sftp_session
    cdef sftp.sftp_limits_t _limits
    cdef public object _open_remote_file_cm

cdef class _RemoteFile:
    cdef sftp.sftp_file _fd
    cdef SFTP _sftp
    cdef str _path
    cdef bint _is_writer
    cdef void _close(self) noexcept

cdef class _PipelinedRemoteFile(_RemoteFile):
    cdef object _aio_queue
    cdef bytearray _drain_buffer
    cdef stdint.uint64_t _read_offset
    cdef _C_AIO _begin_read(self, size_t length)
    cdef _C_AIO _begin_write(self, const unsigned char[:] data)
    cdef void _wait_oldest_write(self) except *
    cdef void _restart_reads(self) except *
    cdef void _discard_in_flight(self) noexcept
    cdef void _close(self) noexcept

cdef class _C_AIO:
    cdef sftp.sftp_aio aio
    cdef size_t length
    cdef bint is_read

    @staticmethod
    cdef _C_AIO from_ptr(sftp.sftp_aio aio, size_t length, bint is_read)
    cdef ssize_t wait_read(self, void* buf, size_t buf_size) noexcept
    cdef ssize_t wait_write(self) noexcept
