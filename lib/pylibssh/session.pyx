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
import inspect
import logging
from cpython.bytes cimport PyBytes_AS_STRING


from pylibssh.channel import Channel
from pylibssh.errors cimport LibsshException, LibsshSessionException
from pylibssh.sftp import SFTP

OPTS_MAP = {
    "host": libssh.SSH_OPTIONS_HOST,
    "user": libssh.SSH_OPTIONS_USER,
    "port": libssh.SSH_OPTIONS_PORT,
    "timeout": libssh.SSH_OPTIONS_TIMEOUT,
    "knownhosts": libssh.SSH_OPTIONS_KNOWNHOSTS,
}
OPTS_DIR_MAP = {
    "ssh_dir": libssh.SSH_OPTIONS_SSH_DIR,
    "add_identity": libssh.SSH_OPTIONS_ADD_IDENTITY,
}

LOG_MAP = {
    logging.NOTSET: libssh.SSH_LOG_NONE,
    logging.DEBUG: libssh.SSH_LOG_DEBUG,
    logging.INFO: libssh.SSH_LOG_INFO,
    logging.WARNING: libssh.SSH_LOG_WARN,
    logging.ERROR: libssh.SSH_LOG_WARN,
    logging.CRITICAL: libssh.SSH_LOG_TRACE
}


cdef class Session:
    def __cinit__(self, host=None, **kwargs):
        self._libssh_session = libssh.ssh_new()
        if self._libssh_session is NULL:
            raise MemoryError
        self._opts = {}

        for key in kwargs:
            self.set_ssh_options(key, kwargs[key])

    def __dealloc__(self):
        if self._libssh_session is not NULL:
            if libssh.ssh_is_connected(self._libssh_session):
                libssh.ssh_disconnect(self._libssh_session)
            libssh.ssh_free(self._libssh_session)
            self._libssh_session = NULL

    @property
    def port(self):
        cdef unsigned int port_i
        if libssh.ssh_options_get_port(self._libssh_session, &port_i) != libssh.SSH_OK:
            return None
        return port_i

    def get_ssh_options(self, key):
        cdef unsigned int port_i
        cdef char *value

        if not key in OPTS_MAP:
            if key in OPTS_DIR_MAP and key in self._opts:
                return self._opts[key]
            raise LibsshException("Unknown attribute name [%s]" % key)
        if key == "port":
            if libssh.ssh_options_get_port(self._libssh_session, &port_i) != libssh.SSH_OK:
                return None
            return port_i
        else:
            if libssh.ssh_options_get(self._libssh_session, OPTS_MAP[key], &value) != libssh.SSH_OK:
                return None
            ret = value.decode()
            libssh.ssh_string_free_char(value)
            return ret

    def set_ssh_options(self, key, value):
        cdef unsigned int port_i

        key_m = None
        if key in OPTS_DIR_MAP:
            key_m = OPTS_DIR_MAP[key]
        elif key in OPTS_MAP:
            key_m = OPTS_MAP[key]
        else:
            raise LibsshException("Unknown attribute name [%s]" % key)
        if key == "port":
            port_i = value
            libssh.ssh_options_set(self._libssh_session, OPTS_MAP["port"], &port_i)
        else:
            if isinstance(value, basestring):
                value = value.encode("utf-8")
            libssh.ssh_options_set(self._libssh_session, key_m, PyBytes_AS_STRING(value))
            if key in OPTS_DIR_MAP:
                self._opts[key] = value

    def connect(self, **kwargs):
        cdef LibsshException saved_execption = None

        for key in kwargs:
            if (key in OPTS_MAP or key in OPTS_DIR_MAP) and (kwargs[key] is not None):
                self.set_ssh_options(key, kwargs[key])

        if libssh.ssh_connect(self._libssh_session) != libssh.SSH_OK:
            libssh.ssh_disconnect(self._libssh_session)
            raise LibsshSessionException("ssh connect failed: %s" % self._get_session_error_str())

        try:
            self.verify_knownhost()
        except Exception:
            libssh.ssh_disconnect(self._libssh_session)
            raise

        # try authenticating with public keys
        try:
            self.authenticate_pubkey()
            return
        except LibsshException as ex:
            saved_execption = ex

        # try authenticating with a password
        if kwargs.get('password'):
            try:
                self.authenticate_password(kwargs["password"])
                return
            except LibsshException as ex:
                saved_execption = ex

        if saved_execption is not None:
            libssh.ssh_disconnect(self._libssh_session)
            raise saved_execption

    @property
    def is_connected(self):
        return self._libssh_session is not NULL and libssh.ssh_is_connected(self._libssh_session)

    def disconnect(self):
        libssh.ssh_disconnect(self._libssh_session)

    def get_server_publickey(self):
        cdef libssh.ssh_key srv_pubkey = NULL
        cdef unsigned char * hash = NULL
        cdef size_t hash_len
        if libssh.ssh_get_server_publickey(self._libssh_session, &srv_pubkey) != libssh.SSH_OK:
            return None
        rc = libssh.ssh_get_publickey_hash(srv_pubkey, libssh.SSH_PUBLICKEY_HASH_SHA1, &hash, &hash_len)
        libssh.ssh_key_free(srv_pubkey)
        if rc != libssh.SSH_OK:
            return None
        cdef char *hash_hex = libssh.ssh_get_hexa(hash, hash_len)
        hash_py = hash_hex.decode("ascii")
        libssh.ssh_string_free_char(hash_hex)
        return hash_py

    def verify_knownhost(self):
        cdef libssh.ssh_known_hosts_e state = libssh.ssh_session_is_known_server(self._libssh_session)
        if state == libssh.SSH_KNOWN_HOSTS_OK:
            return True
        hash = self.get_server_publickey()
        if state == libssh.SSH_KNOWN_HOSTS_ERROR:
            raise LibsshException("verify know host failed: %s" % self._get_session_error_str())

        msg_map = {
            libssh.SSH_KNOWN_HOSTS_CHANGED: "Host key for server has changed: " + hash,
            libssh.SSH_KNOWN_HOSTS_OTHER: "Host key type for server has changed: " + hash,
            libssh.SSH_KNOWN_HOSTS_NOT_FOUND: "Host file not found",
            libssh.SSH_KNOWN_HOSTS_UNKNOWN: "Host is unknown: " + hash,
        }
        raise LibsshException(msg_map[state])

    def authenticate_pubkey(self):
        cdef int rc
        rc = libssh.ssh_userauth_publickey_auto(self._libssh_session, NULL, NULL)
        if rc != libssh.SSH_AUTH_SUCCESS:
            raise LibsshException("Failed to authenticate public key: %s" % self._get_session_error_str())

    def authenticate_password(self, password):
        cdef int rc
        rc = libssh.ssh_userauth_password(self._libssh_session, NULL, password.encode())
        if rc == libssh.SSH_AUTH_ERROR or rc == libssh.SSH_AUTH_DENIED:
            raise LibsshException("Failed to authenticate with password: %s" % self._get_session_error_str())

    def new_channel(self):
        return Channel(self)

    def new_shell_channel(self):
        channel = Channel(self)
        channel.request_shell()
        return channel

    def invoke_shell(self):
        return self.new_shell_channel()

    def sftp(self):
        return SFTP(self)

    def set_log_level(self, level):
        if level in LOG_MAP.keys():
            rc = libssh.ssh_set_log_level(LOG_MAP[level])
            if rc != libssh.SSH_OK:
                raise LibsshException("Failed to set log level [%d] with error [%d]" % (level, rc))
        else:
            raise LibsshException("Invalid log level [%d]" % level)

    def close(self):
        if self._libssh_session is not NULL:
            if libssh.ssh_is_connected(self._libssh_session):
                libssh.ssh_disconnect(self._libssh_session)
            libssh.ssh_free(self._libssh_session)
            self._libssh_session = NULL

    def _get_session_error_str(self):
        return libssh.ssh_get_error(<void*>self._libssh_session).decode()

cdef libssh.ssh_session get_libssh_session(Session session):
    return session._libssh_session
