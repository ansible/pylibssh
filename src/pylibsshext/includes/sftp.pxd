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
from posix.types cimport mode_t

from libc cimport stdint

from pylibsshext.includes.libssh cimport ssh_channel, ssh_session, ssh_string


cdef extern from "libssh/sftp.h" nogil:

    struct sftp_session_struct:
        pass
    ctypedef sftp_session_struct * sftp_session

    struct sftp_file_struct:
        pass
    ctypedef sftp_file_struct * sftp_file

    struct sftp_attributes_struct:
        char *name
        char *longname
        stdint.uint32_t flags
        stdint.uint8_t type
        stdint.uint64_t size
        stdint.uint32_t uid
        stdint.uint32_t gid
        char *owner
        char *group
        stdint.uint32_t permissions
        stdint.uint64_t atime64
        stdint.uint32_t atime
        stdint.uint32_t atime_nseconds
        stdint.uint64_t createtime
        stdint.uint32_t createtime_nseconds
        stdint.uint64_t mtime64
        stdint.uint32_t mtime
        stdint.uint32_t mtime_nseconds
        ssh_string acl
        stdint.uint32_t extended_count
        ssh_string extended_type
        ssh_string extended_data
    ctypedef sftp_attributes_struct * sftp_attributes

    cdef int SSH_FX_OK
    cdef int SSH_FX_EOF
    cdef int SSH_FX_NO_SUCH_FILE
    cdef int SSH_FX_PERMISSION_DENIED
    cdef int SSH_FX_FAILURE
    cdef int SSH_FX_BAD_MESSAGE
    cdef int SSH_FX_NO_CONNECTION
    cdef int SSH_FX_CONNECTION_LOST
    cdef int SSH_FX_OP_UNSUPPORTED
    cdef int SSH_FX_INVALID_HANDLE
    cdef int SSH_FX_NO_SUCH_PATH
    cdef int SSH_FX_FILE_ALREADY_EXISTS
    cdef int SSH_FX_WRITE_PROTECT
    cdef int SSH_FX_NO_MEDIA

    sftp_session sftp_new(ssh_session session)
    int sftp_init(sftp_session sftp)
    void sftp_free(sftp_session sftp)

    sftp_file sftp_open(sftp_session session, const char *file, int accesstype, mode_t mode)
    int sftp_close(sftp_file file)
    ssize_t sftp_write(sftp_file file, const void *buf, size_t count)
    ssize_t sftp_read(sftp_file file, const void *buf, size_t count)
    int sftp_get_error(sftp_session sftp)

    sftp_attributes sftp_stat(sftp_session session, const char *path)


cdef extern from "sys/stat.h" nogil:
    cdef int S_IRWXU
