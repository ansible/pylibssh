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

from pylibsshext.channel import Channel
from pylibsshext.errors cimport LibsshSessionException
from pylibsshext.scp import SCP
from pylibsshext.sftp import SFTP


OPTS_MAP = {
    "fd": libssh.SSH_OPTIONS_FD,
    "host": libssh.SSH_OPTIONS_HOST,
    "user": libssh.SSH_OPTIONS_USER,
    "port": libssh.SSH_OPTIONS_PORT,
    "timeout": libssh.SSH_OPTIONS_TIMEOUT,
    "knownhosts": libssh.SSH_OPTIONS_KNOWNHOSTS,
    "proxycommand": libssh.SSH_OPTIONS_PROXYCOMMAND,
    "gssapi_server_identity": libssh.SSH_OPTIONS_GSSAPI_SERVER_IDENTITY,
    "gssapi_client_identity": libssh.SSH_OPTIONS_GSSAPI_CLIENT_IDENTITY,
    "gssapi_delegate_credentials": libssh.SSH_OPTIONS_GSSAPI_DELEGATE_CREDENTIALS,
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

KNOW_HOST_MSG_MAP = {
    libssh.SSH_KNOWN_HOSTS_CHANGED: "Host key for server has changed: ",
    libssh.SSH_KNOWN_HOSTS_OTHER: "Host key type for server has changed: ",
    libssh.SSH_KNOWN_HOSTS_UNKNOWN: "Host is unknown: "
}

HOST_KEY_AUTO_ADD_MSG_MAP = {
    libssh.SSH_AUTH_ERROR: " A serious error happened.",
    libssh.SSH_AUTH_DENIED: "The server doesn't accept that public key as an authentication token. Try another key or another method.",
    libssh.SSH_AUTH_PARTIAL: "You've been partially authenticated, you still have to use another method.",
    libssh.SSH_AUTH_AGAIN: "In nonblocking mode, you've got to call this again later."
}


class MissingHostKeyPolicy(object):
    """
    Interface for defining the policy that `.SSHClient` should use when the
    SSH server's hostname is not in either the system host keys or the
    application's keys.
    """
    def missing_host_key(self, session, hostname, username, key_type, fingerprint, message):
        """
        Called when an `.Session` receives a server key for a server that
        isn't in either the system or local known host.  To accept
        the key, simply return.  To reject, raised an exception (which will
        be passed to the calling application).
        """
        pass


class AutoAddPolicy(MissingHostKeyPolicy):
    """
    Policy for automatically adding the hostname and new host key.
    """

    def missing_host_key(self, session, hostname, username, key_type, fingerprint, message):
        return session.hostkey_auto_add(username)


class RejectPolicy(MissingHostKeyPolicy):
    """
    Policy for automatically rejecting the unknown hostname & key.
    """

    def missing_host_key(self, session, hostname, username, key_type, fingerprint, message):
        raise LibsshSessionException(message)


cdef class Session(object):
    def __init__(self, host=None, **kwargs):
        self._policy = RejectPolicy()
        self._hash_py = None
        self._fingerprint_py = None
        self._keytype_py = None

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

        if key not in OPTS_MAP:
            if key in OPTS_DIR_MAP and key in self._opts:
                return self._opts[key]
            raise LibsshSessionException("Unknown attribute name [%s]" % key)
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
        cdef int value_int
        cdef unsigned int value_uint
        cdef long value_long

        key_m = None
        if key in OPTS_DIR_MAP:
            key_m = OPTS_DIR_MAP[key]
        elif key in OPTS_MAP:
            key_m = OPTS_MAP[key]
        else:
            raise LibsshSessionException("Unknown attribute name [%s]" % key)
        if key in ("fd", "gssapi_delegate_credentials"):
            value_int = value
            libssh.ssh_options_set(self._libssh_session, key_m, &value_int)
        elif key == "port":
            value_uint = value
            libssh.ssh_options_set(self._libssh_session, key_m, &value_uint)
        elif key == "timeout":
            value_long = value
            libssh.ssh_options_set(self._libssh_session, key_m, &value_long)
        else:
            if isinstance(value, basestring):
                value = value.encode("utf-8")
            libssh.ssh_options_set(self._libssh_session, key_m, PyBytes_AS_STRING(value))
            if key in OPTS_DIR_MAP:
                self._opts[key] = value

    def connect(self, **kwargs):
        """Conenct to ssh server and negotiate libssh session by
        optionally verifying the server's host key and authenticate
        either by password or private key.

        :param fd: The file descriptor of the socket to use for the connection.
        :type fd: int

        :param host: The address of the remote host
        :type host: str

        :param user: The username to authenticate with
        :type user: str

        :param look_for_keys: Flag to enable searching for private keys in ``~/.ssh/``.
        The default is set to True.
        :type look_for_keys: boolean

        :param private_key: A private key to authenticate the SSH session.
        :type private_key: bytes

        :param private_key_password: A password for the private key.
        :type private_key_password: bytes

        :param password: The password to authenticate the ssh session.
        :type password: str

        :param password_prompt: The prompt to look for when using password authentication.
        :type password_prompt: str

        :param gssapi_server_identity: The service principal hostname to use.
        For example for principal ``host/file.example.com@EXAMPLE.COM``, the hostname
        would be ``file.example.com``. Not required for GSSAPI authentication.
        :type gssapi_server_identity: str

        :param gssapi_client_identity: The client principal name to use.
        For example for principal ``user@EXAMPLE.COM``, the name would be ``user``.
        Not required for GSSAPI authentication.
        :type gssapi_server_identity: str

        :param gssapi_delegate_credentials: Whether to forward your GSSAPI
        identity to the remote server for use to connect from there to other
        remote hosts. This is the equivalent of SSH Agent forwarding for GSSAPI.
        The default is set to False.
        :type gssapi_delegate_credentials: boolean

        :param host_key_checking: The flag to control is the server key in knownhosts
        file should be validated. It defaults to True
        :type host_key_checking: boolean

        :param timeout: The timeout in seconds for the TCP connect
        :type timeout: long integer

        :param port: The ssh server port to connect to
        :type port: integer

        :param proxycommand: The proxycommand use to setup a ssh connection using
        jumphost
        :type proxycommand: str
        """
        cdef LibsshSessionException saved_exception = None

        for key in kwargs:
            if (key in OPTS_MAP or key in OPTS_DIR_MAP) and (kwargs[key] is not None):
                self.set_ssh_options(key, kwargs[key])

        if libssh.ssh_connect(self._libssh_session) != libssh.SSH_OK:
            libssh.ssh_disconnect(self._libssh_session)
            raise LibsshSessionException("ssh connect failed: %s" % self._get_session_error_str())
        if kwargs.get('host_key_checking', True):
            try:
                self.verify_knownhost()
            except Exception:
                libssh.ssh_disconnect(self._libssh_session)
                raise

        # We need to userauth_none before we can query the available auth types
        rc = libssh.ssh_userauth_none(self._libssh_session, NULL)
        if rc == libssh.SSH_AUTH_SUCCESS:
            # Huh, it worked?
            return
        if rc == libssh.SSH_AUTH_ERROR:
            raise LibsshSessionException("Error while fetching list of supported authentication methods")

        supported_auth = libssh.ssh_userauth_list(self._libssh_session, NULL)

        if kwargs.get('private_key') and supported_auth & libssh.SSH_AUTH_METHOD_PUBLICKEY:
            # try authenticating with a given private key
            try:
                self.authenticate_specific_pubkey(
                    kwargs['private_key'],
                    kwargs.get('private_key_password'),
                )
            except LibsshSessionException as ex:
                saved_exception = ex
            else:
                return

        if kwargs.get('password') and supported_auth & libssh.SSH_AUTH_METHOD_PASSWORD:
            # try authenticating with a password
            try:
                self.authenticate_password(kwargs["password"])
            except LibsshSessionException as ex:
                saved_exception = ex
            else:
                return

        if kwargs.get('password') and supported_auth & libssh.SSH_AUTH_METHOD_INTERACTIVE:
            # try authenticating with keyboard-interactive
            # This will be neither user-interactive nor involve a keyboard,
            # but rather emulate the exchange using the provided password
            try:
                self.authenticate_interactive(kwargs["password"], expected_prompt=kwargs.get("password_prompt"))
            except LibsshSessionException as ex:
                saved_exception = ex
            else:
                return

        if kwargs.get('look_for_keys', True) and supported_auth & libssh.SSH_AUTH_METHOD_PUBLICKEY:
            # try authenticating with public keys
            try:
                self.authenticate_pubkey()
            except LibsshSessionException as ex:
                saved_exception = ex
            else:
                return

        if supported_auth & libssh.SSH_AUTH_METHOD_GSSAPI_MIC:
            # try authenticating with GSSAPI with mic
            try:
                self.authenticate_gssapi_with_mic()
            except LibsshSessionException as ex:
                saved_exception = ex
            else:
                return

        if saved_exception is not None:
            libssh.ssh_disconnect(self._libssh_session)
            raise saved_exception
        raise LibsshSessionException("Failed to find any acceptable way to authenticate")

    @property
    def is_connected(self):
        return self._libssh_session is not NULL and libssh.ssh_is_connected(self._libssh_session)

    def disconnect(self):
        libssh.ssh_disconnect(self._libssh_session)

    def _load_server_publickey(self):
        cdef libssh.ssh_key srv_pubkey = NULL
        cdef unsigned char * hash = NULL
        cdef size_t hash_len

        rc = libssh.ssh_get_server_publickey(self._libssh_session, &srv_pubkey)
        if rc != libssh.SSH_OK:
            return

        rc = libssh.ssh_get_publickey_hash(srv_pubkey, libssh.SSH_PUBLICKEY_HASH_SHA1, &hash, &hash_len)

        cdef libssh.ssh_keytypes_e key_type = libssh.ssh_key_type(srv_pubkey)
        cdef const char * keytype_hex = libssh.ssh_key_type_to_char(key_type)

        if keytype_hex is not NULL:
            self._keytype_py = keytype_hex.decode("ascii")

        libssh.ssh_key_free(srv_pubkey)

        if rc != libssh.SSH_OK:
            return

        cdef char * hash_hex = libssh.ssh_get_hexa(hash, hash_len)
        cdef char * fingerprint_hex = libssh.ssh_get_fingerprint_hash(libssh.SSH_PUBLICKEY_HASH_SHA1,
                                                                      hash, hash_len)

        self._hash_py = hash_hex.decode("ascii")
        self._fingerprint_py = fingerprint_hex.decode("ascii")

        libssh.ssh_string_free_char(<char *>hash_hex)
        libssh.ssh_string_free_char(fingerprint_hex)

    def hostkey_auto_add(self, username):
        rc = libssh.ssh_session_update_known_hosts(self._libssh_session)
        if rc != libssh.SSH_OK:
            raise LibsshSessionException("host key auto add failed: %s" % self._get_session_error_str())

    def verify_knownhost(self):
        cdef libssh.ssh_known_hosts_e state = libssh.ssh_session_is_known_server(self._libssh_session)

        if state == libssh.SSH_KNOWN_HOSTS_OK:
            return True
        self._load_server_publickey()

        if state == libssh.SSH_KNOWN_HOSTS_ERROR:
            raise LibsshSessionException("verify know host failed: %s" % self._get_session_error_str())

        if state == libssh.SSH_KNOWN_HOSTS_NOT_FOUND:
            raise LibsshSessionException("Host file not found: %s" % self._get_session_error_str())

        know_host_msg = KNOW_HOST_MSG_MAP[state] + self._hash_py
        self._policy.missing_host_key(self,
                                      self.get_ssh_options('host'),
                                      self.get_ssh_options('user'),
                                      self._keytype_py,
                                      self._fingerprint_py,
                                      know_host_msg)

    def authenticate_specific_pubkey(
            self,
            bytes private_key_b64 not None,
            private_key_password=None,
    ):
        """Authenticate this session using a private key.

        If a password is provided, it'll be used to decrypt the key.

        :param private_key_b64: A private key.
        :type private_key_b64: bytes

        :param private_key_password: A password for the private key \
                                     (if it's protected), defaults to \
                                     no password.
        :type private_key_password: bytes, optional

        :raises LibsshSessionException: If authentication failed.

        :return: Nothing.
        :rtype: NoneType
        """
        cdef const char *c_private_key_b64 = private_key_b64
        cdef bytes b_password
        cdef const char *c_password = NULL
        cdef libssh.ssh_key _private_key
        cdef int rc
        if private_key_password is not None:
            if isinstance(private_key_password, bytes):
                b_password = private_key_password
            else:
                b_password = private_key_password.encode()
            c_password = b_password
        libssh.ssh_pki_import_privkey_base64(
            c_private_key_b64, c_password,
            NULL, NULL,
            &_private_key,
        )

        rc = libssh.ssh_userauth_publickey(
            self._libssh_session, NULL, _private_key,
        )

        if rc != libssh.SSH_AUTH_SUCCESS:
            raise LibsshSessionException(
                "Failed to authenticate a specific public key: "
                "{!s} (RC={!r})".
                format(self._get_session_error_str(), rc),
            )
        libssh.ssh_key_free(_private_key)

    def authenticate_pubkey(self):
        cdef int rc
        rc = libssh.ssh_userauth_publickey_auto(self._libssh_session, NULL, NULL)
        if rc != libssh.SSH_AUTH_SUCCESS:
            raise LibsshSessionException("Failed to authenticate public key: %s" % self._get_session_error_str())

    def authenticate_password(self, password):
        cdef int rc
        rc = libssh.ssh_userauth_password(self._libssh_session, NULL, password.encode())
        if rc == libssh.SSH_AUTH_ERROR or rc == libssh.SSH_AUTH_DENIED:
            raise LibsshSessionException("Failed to authenticate with password: %s" % self._get_session_error_str())

    def authenticate_interactive(self, password, expected_prompt=None):
        """Authenticate this session using keyboard-interactive authentication.

        :param password: The password to authenticate with.
        :type password: str

        :param expected_prompt: The expected password prompt.
        :type expected_prompt: str

        :raises LibsshSessionException: If authentication failed.

        :return: Nothing.
        :rtype: NoneType
        """
        cdef int rc
        cdef char should_echo
        if expected_prompt is None:
            expected_prompt = "password:"
        expected_prompt = expected_prompt.lower().strip()
        rc = libssh.ssh_userauth_kbdint(self._libssh_session, NULL, NULL)

        while rc == libssh.SSH_AUTH_INFO:
            prompt_count = libssh.ssh_userauth_kbdint_getnprompts(self._libssh_session)
            prompt_text_list = []
            if prompt_count > 0:
                for prompt in range(prompt_count):
                    prompt_text = libssh.ssh_userauth_kbdint_getprompt(self._libssh_session, prompt, &should_echo)
                    prompt_text = prompt_text.decode().lower().strip()
                    prompt_text_list.append(prompt_text)
                    if prompt_text.lower().strip().endswith(expected_prompt):
                        break
                else:
                    raise LibsshSessionException("None of the prompts looked like password prompts: {err}".format(err=prompt_text_list))
                rc = libssh.ssh_userauth_kbdint_setanswer(self._libssh_session, prompt, password.encode())

            # We need to keep calling ssh_userauth_kbdint until it stops returning SSH_AUTH_INFO
            # (ie, asking for more information and has made a decison as to whether we are allowed in)
            rc = libssh.ssh_userauth_kbdint(self._libssh_session, NULL, NULL)

        if rc in (libssh.SSH_AUTH_ERROR, libssh.SSH_AUTH_DENIED):
            raise LibsshSessionException("Failed to authenticate with keyboard-interactive: {err}".format(err=self._get_session_error_str()))

    def authenticate_gssapi_with_mic(self):
        """Authenticate this session using gssapi-with-mic authentication.

        :raises LibsshSessionException: If authentication failed.

        :return: Nothing.
        :rtype: NoneType
        """
        cdef int rc
        rc = libssh.ssh_userauth_gssapi(self._libssh_session)

        if rc in (libssh.SSH_AUTH_ERROR, libssh.SSH_AUTH_DENIED):
            raise LibsshSessionException("Failed to authenticate with gssapi-with-mic: {err}".format(err=self._get_session_error_str()))

    def new_channel(self):
        return Channel(self)

    def new_shell_channel(self):
        channel = Channel(self)
        channel.request_shell()
        return channel

    def invoke_shell(self):
        return self.new_shell_channel()

    def scp(self):
        return SCP(self)

    def sftp(self):
        return SFTP(self)

    def set_log_level(self, level):
        if level in LOG_MAP.keys():
            rc = libssh.ssh_set_log_level(LOG_MAP[level])
            if rc != libssh.SSH_OK:
                raise LibsshSessionException("Failed to set log level [%d] with error [%d]" % (level, rc))
        else:
            raise LibsshSessionException("Invalid log level [%d]" % level)

    def close(self):
        if self._libssh_session is not NULL:
            if libssh.ssh_is_connected(self._libssh_session):
                libssh.ssh_disconnect(self._libssh_session)
            libssh.ssh_free(self._libssh_session)
            self._libssh_session = NULL

    def set_missing_host_key_policy(self, policy):
        """The policy to use if the know host key is missing.
        """
        if inspect.isclass(policy):
            policy = policy()
        self._policy = policy

    def _get_session_error_str(self):
        return libssh.ssh_get_error(<void*>self._libssh_session).decode()


cdef libssh.ssh_session get_libssh_session(Session session):
    return session._libssh_session
