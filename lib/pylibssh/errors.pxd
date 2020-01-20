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
from pylibssh.includes cimport libssh

cdef class LibsshException(Exception):
    pass

cdef class LibsshSessionException(LibsshException):
    pass

cdef class LibsshChannelException(LibsshException):
    pass

cdef class LibsshSFTPException(LibsshException):
    pass
