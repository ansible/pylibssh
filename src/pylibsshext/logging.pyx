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

"""
The logging module of ``ansible-pylibssh`` provides interface between libssh
logging and Python :external+python:mod:`logging` facility.

It provides two new log levels, that can be used with to set the log verbosity
using ``set_log_level()`` method on ``Session`` object.

.. data:: ANSIBLE_PYLIBSSH_NOLOG

    Indicates that ``ansible-pylibssh`` will not emit any events into the
    :external+python:mod:`logging` subsystem.

.. data:: ANSIBLE_PYLIBSSH_TRACE

    Indicates that ``ansible-pylibssh`` will make all possible logs available
    to the :external+python:mod:`logging` subsystem, generally useful for
    debugging low-level libssh operations.

The default log level is set to the ``ANSIBLE_PYLIBSSH_TRACE``, which means
all the messages are fed into the python. Setting different levels from
the above lost or any value from Python :external+python:mod:`logging` module
will allow prevent libssh emitting these logs.
"""

import logging

from pylibsshext.errors cimport LibsshSessionException
from pylibsshext.includes cimport callbacks, libssh


ANSIBLE_PYLIBSSH_NOLOG = logging.FATAL * 2
ANSIBLE_PYLIBSSH_TRACE = int(logging.DEBUG / 2)

LOG_MAP = {
    ANSIBLE_PYLIBSSH_TRACE: libssh.SSH_LOG_TRACE,
    logging.DEBUG: libssh.SSH_LOG_DEBUG,
    logging.INFO: libssh.SSH_LOG_INFO,
    logging.WARNING: libssh.SSH_LOG_WARN,
    ANSIBLE_PYLIBSSH_NOLOG: libssh.SSH_LOG_NONE,
}

LOG_MAP_REV = {
    **{
        libssh_name: py_name
        for py_name, libssh_name in LOG_MAP.items()
    },
}

# mapping aliases
LOG_MAP[logging.NOTSET] = libssh.SSH_LOG_TRACE
LOG_MAP[logging.ERROR] = libssh.SSH_LOG_WARN
LOG_MAP[logging.CRITICAL] = libssh.SSH_LOG_WARN


def _add_trace_log_level():
    """
    Add a trace log level to the Python :external+python:mod:`logging` system.
    """
    level_num = ANSIBLE_PYLIBSSH_TRACE
    level_name = "TRACE"

    logging.addLevelName(level_num, level_name)


cdef void _pylibssh_log_wrapper(int priority,
                                const char *function,
                                const char *buffer,
                                void *userdata) noexcept:
    log_level = LOG_MAP_REV[priority]
    logging.getLogger("ansible-pylibssh").log(log_level, buffer.decode('utf-8'))


def _set_log_callback():
    """
    Set libssh logging callback

    Our function redirects the messages to python
    :external+python:mod:`logging` facility.
    """
    # Note, that we could also set the set_log_userdata() to access the logger
    # object, but I did not find it much useful when it is global already.
    callbacks.ssh_set_log_callback(_pylibssh_log_wrapper)


def _initialize_logging():
    """
    Initialize libssh logging subsystem

    This is implemenbed by adding our own log level and registering our callback
    with libssh.
    """
    # This is done globally, as the libssh logging is not tied to specific
    # session (its thread-local state in libssh) so either very good care
    # needs to be taken to make sure the logger is in place when callback
    # can be called almost from anywhere in the code or just keep it global.
    _add_trace_log_level()
    _set_log_callback()


def _set_level(level):
    """
    Set logging level to the given value from ``LOG_MAP``.

    :param level: The level to set.
    :type level: int

    :raises LibsshSessionException: If the log level is not known to libssh or pylibssh.

    :returns: Nothing.
    :rtype: None
    """
    if level not in LOG_MAP:
        raise LibsshSessionException(f'Invalid log level [{level:d}]')

    # can never fail for valid values from the map
    libssh.ssh_set_log_level(LOG_MAP[level])
