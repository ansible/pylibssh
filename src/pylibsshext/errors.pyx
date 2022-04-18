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
cdef class LibsshException(Exception):
    def __init__(self, message=''):
        self.message = message
        super(LibsshException, self).__init__(message)

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message

    def _get_session_error_str(self, obj):
        return libssh.ssh_get_error(<void*>obj._libssh_session).decode()


cdef class LibsshSessionException(LibsshException):
    pass


cdef class LibsshChannelException(LibsshException):
    pass


class LibsshChannelReadFailure(LibsshChannelException, ConnectionError):
    """Raised when there is a failure to read from a libssh channel."""


cdef class LibsshSCPException(LibsshException):
    pass


cdef class LibsshSFTPException(LibsshException):
    pass
