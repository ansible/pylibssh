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
#
from posix.types cimport mode_t

from pylibsshext.includes.libssh cimport ssh_session, ssh_channel


cdef extern from "libssh/sftp.h" nogil:

    struct sftp_session_struct:
        pass
    ctypedef sftp_session_struct * sftp_session

    struct sftp_file_struct:
        pass
    ctypedef sftp_file_struct * sftp_file

    sftp_session sftp_new(ssh_session session)
    int sftp_init(sftp_session sftp)
    void sftp_free(sftp_session sftp)

    sftp_file sftp_open(sftp_session session, const char *file, int accesstype, mode_t mode)
    int sftp_close(sftp_file file)
    ssize_t sftp_write(sftp_file file, const void *buf, size_t count)

cdef extern from "sys/stat.h" nogil:
    cdef int S_IRWXU
